import asyncio
from asyncio import subprocess
from asyncio.subprocess import PIPE
from datetime import datetime
from dotenv import load_dotenv
import json
import os
from pathlib import Path
from rdflib import Graph, Literal, RDF, URIRef, BNode
import tempfile
from .pp_analyze import bulk_analyze_pp, analyze_pp_from_website_name
from . import kg, dtou
from .dtou import NS_DTOU, NS_EX
from .utils import dict_equal, dict_hash


load_dotenv()


_DTOU_LANG_DIR = Path(os.getenv("DTOU_LANG_DIR")) if os.getenv("DTOU_LANG_DIR") else (Path(os.path.realpath(__file__)).parent.parent / 'third_party' / 'dtou-lang')

_CACHE_DIR_NAME = 'eye-result-cache'
cache_dir = os.getenv("QUERY_CACHE_DIR")
cache_dir_path = Path(cache_dir) / _CACHE_DIR_NAME if cache_dir else None
if cache_dir_path and not cache_dir_path.exists():
    cache_dir_path.mkdir(parents=True)


A = RDF.type


def get_user_persona(persona_dir: str|None = None):
    if not persona_dir:
        if os.getenv("USER_PERSONA_DIR") is None:
            raise ValueError("USER_PERSONA_DIR not set in .env")
        persona_dir = Path(os.getenv("USER_PERSONA_DIR"))
    path_persona = Path(persona_dir)
    res = []
    for persona_file in sorted(path_persona.glob("*.ttl")):
        with open(persona_file, "r") as f:
            res.append(f.read())
    return res


def convert_practices_to_app_policy(data_practices: list, app_name, first_party_name):
    app_policy = dtou.convert_to_app_policy(data_practices, app_name, first_party_name)
    app_policy_graph = app_policy.to_rdf()
    policy_node = app_policy_graph.value(None, A, NS_DTOU['AppPolicy'])
    app_policy_turtle = app_policy_graph.serialize()
    return app_policy_turtle, policy_node


def get_dummy_context(app_policy_node: URIRef):
    g = Graph()
    g.bind('dtou', NS_DTOU)
    g.bind('ex', NS_EX)
    g.add((NS_EX['usageContext1'], A, NS_DTOU['UsageContext']))
    g.add((NS_EX['usageContext1'], NS_DTOU['user'], NS_EX['someone']))
    g.add((NS_EX['someone'], A, NS_DTOU['User']))
    n_app_info = BNode()
    g.add((NS_EX['usageContext1'], NS_DTOU['app'], n_app_info))
    g.add((n_app_info, A, NS_DTOU['AppInfo']))
    g.add((n_app_info, NS_DTOU['policy'], app_policy_node))
    g.add((NS_EX['usageContext1'], NS_DTOU['time'], Literal(datetime.now().strftime("%Y%m%d"))))
    return g.serialize(format='turtle')

_sem_dir_creation = asyncio.Semaphore(1)

async def guarantee_cache_dir(website_url: str):
    if cache_dir_path:
        website_cache_dir = cache_dir_path / website_url
        if not website_cache_dir.exists():
            async with _sem_dir_creation:
                if not website_cache_dir.exists():
                    website_cache_dir.mkdir(parents=True)


def get_cache_file(cache_dir_path: Path, query_content: dict, website: str):
    query_hash = dict_hash(query_content)
    return cache_dir_path / website / f"{query_hash}.json"


async def get_cached_result(cache_dir_path: Path, query_content: dict, website: str):
    file_path = get_cache_file(cache_dir_path, query_content, website)
    if not file_path.exists():
        raise FileNotFoundError(f"Cache file not found: {file_path}")
    with open(file_path, 'r') as f:
        content = json.load(f)
        return content['reasoning_result'], content['reasoning_errors']


async def is_cached(cache_dir_path: Path, query_content: dict, website: str):
    try:
        content = await get_cached_result(cache_dir_path, query_content, website)
        # if dict_equal(content['query_content'], query_content):
        #     return True
        return True
    except FileNotFoundError:
        pass
    return False


async def insert_to_cache(cache_dir_path: Path, query_content: dict, website: str, reasoning_result: str, reasoning_errors: str):
    content = {
        'query_content': query_content,
        'reasoning_result': reasoning_result,
        'reasoning_errors': reasoning_errors,
    }
    await guarantee_cache_dir(website)
    with open(get_cache_file(cache_dir_path, query_content, website), 'w') as f:
        json.dump(content, f)


async def run_reasoning(user_persona, app_policy, app_policy_node, website_url, override_cache = False) -> tuple[str, str]:
    '''
    Call external eye reasoner to perform the reasoning, and return the result (stdout) of the reasoner.
    Internally, it uses subprocess to call the external reasoner.
    '''

    reasoner_exec = os.getenv("EYE_REASONER_EXEC")
    if reasoner_exec is None:
        reasoner_exec = "eye"
    dtou_reasoner_files = list(map(str, [
        _DTOU_LANG_DIR / 'dtou-lang-reasoning.n3',
    ]))
    query_file = _DTOU_LANG_DIR / 'query-pp-analyze.n3'

    additional_rules_dir = os.getenv("ADDITIONAL_REASONING_RULES")
    additional_rules = []
    if additional_rules_dir:
        for f in Path(additional_rules_dir).iterdir():
            if f.is_file():
                additional_rules.append(str(f))

    dummy_context = get_dummy_context(app_policy_node)

    query_content = {
        'user_persona': user_persona,
        'website_url': website_url,
        'dtou_reasoner_files': sorted(dtou_reasoner_files),
        'additional_rules': sorted(additional_rules),
        'query_file': str(query_file),
    }

    if not override_cache:
        if cache_dir_path and await is_cached(cache_dir_path, query_content, website_url):
            return await get_cached_result(cache_dir_path, query_content, website_url)

    with tempfile.NamedTemporaryFile('w', suffix='.ttl') as user_persona_file, tempfile.NamedTemporaryFile('w', suffix='.ttl') as app_policy_file, tempfile.NamedTemporaryFile('w', suffix='.ttl') as context_file:
        user_persona_file.write(user_persona)
        user_persona_file.flush()
        app_policy_file.write(app_policy)
        app_policy_file.flush()
        context_file.write(dummy_context)
        context_file.flush()
        p = await asyncio.create_subprocess_exec(reasoner_exec, '--quiet', '--nope', *dtou_reasoner_files, user_persona_file.name, app_policy_file.name, context_file.name, *additional_rules, '--query', query_file, stdout=PIPE, stderr=PIPE)
        out, err = await p.communicate()
        # p = subprocess.Popen([reasoner_exec, '--quiet', '--nope', *dtou_reasoner_files, user_persona_file.name, app_policy_file.name, context_file.name, *additional_rules, '--query', query_file], stdout=PIPE, stderr=PIPE)
        # out, err = p.communicate()

        out_d = out.decode('utf-8')
        err_d = err.decode('utf-8')

        if cache_dir_path:
            await insert_to_cache(cache_dir_path, query_content, website_url, out_d, err_d)

        return out_d, err_d


async def analyze_pp_with_user_persona(website_url: str, website_name: str, data_practices: list|None = None, user_persona_dir: str|None = None, override_cache: bool = False):
    user_persona_list = get_user_persona(persona_dir=user_persona_dir)
    user_persona = '\n'.join(user_persona_list)
    if not data_practices:
        data_practices, errs = analyze_pp_from_website_name(website_url)
    if not data_practices:
        raise ValueError(f"No data practices found for {website_url}")
    app_policy, app_policy_node = convert_practices_to_app_policy(data_practices, website_url, website_name)
    reasoning_result, err = await run_reasoning(user_persona, app_policy, app_policy_node, website_url, override_cache=override_cache)
    g = Graph()
    g.parse(data=reasoning_result, format='turtle')
    return g, err
