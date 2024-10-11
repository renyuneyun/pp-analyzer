from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path
from rdflib import Graph, Literal, RDF, URIRef, BNode
import subprocess
from subprocess import PIPE
import tempfile
from .pp_analyze import bulk_analyze_pp, analyze_pp_from_website_name
from . import kg, dtou
from .dtou import NS_DTOU, NS_EX


load_dotenv()


_DTOU_LANG_DIR = Path(os.getenv("DTOU_LANG_DIR")) if os.getenv("DTOU_LANG_DIR") else (Path(os.path.realpath(__file__)).parent.parent / 'third_party' / 'dtou-lang')


A = RDF.type


def get_user_persona(persona_dir: str|None = None):
    if not persona_dir:
        if os.getenv("USER_PERSONA_DIR") is None:
            raise ValueError("USER_PERSONA_DIR not set in .env")
        persona_dir = Path(os.getenv("USER_PERSONA_DIR"))
    path_persona = Path(persona_dir)
    res = []
    for persona_file in path_persona.glob("*.ttl"):
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


def run_reasoning(user_persona, app_policy, app_policy_node):
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

    dummy_context = get_dummy_context(app_policy_node)

    with tempfile.NamedTemporaryFile('w', suffix='.ttl') as user_persona_file, tempfile.NamedTemporaryFile('w', suffix='.ttl') as app_policy_file, tempfile.NamedTemporaryFile('w', suffix='.ttl') as context_file:
        user_persona_file.write(user_persona)
        user_persona_file.flush()
        app_policy_file.write(app_policy)
        app_policy_file.flush()
        context_file.write(dummy_context)
        context_file.flush()
        p = subprocess.Popen([reasoner_exec, '--quiet', '--nope', *dtou_reasoner_files, user_persona_file.name, app_policy_file.name, context_file.name, '--query', query_file], stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out.decode('utf-8'), err.decode('utf-8')


def analyze_pp_with_user_persona(website_url: str, website_name: str, data_practices: list|None = None, user_persona_dir: str|None = None):
    user_persona_list = get_user_persona(persona_dir=user_persona_dir)
    user_persona = '\n'.join(user_persona_list)
    if not data_practices:
        data_practices, errs = analyze_pp_from_website_name(website_url)
    if not data_practices:
        raise ValueError(f"No data practices found for {website_url}")
    app_policy, app_policy_node = convert_practices_to_app_policy(data_practices, website_url, website_name)
    reasoning_result, err = run_reasoning(user_persona, app_policy, app_policy_node)
    g = Graph()
    g.parse(data=reasoning_result, format='turtle')
    return g, err
