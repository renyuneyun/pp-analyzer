import asyncio
from asyncio import Semaphore
from collections import defaultdict
from pathlib import Path
from rdflib import Graph, RDF
from tqdm.auto import tqdm
import pp_analyze
from pp_analyze import user_preference_analyze as upa
from pp_analyze.data_model import DataEntity, PurposeEntity
from .dtou import NS_DTOU
from .kg import NS
from .pp_analyze import get_relative_file_path_for_pp


def get_pesonas_under_dir(persona_base_dir) -> list[str]:
    simple_persona_dir = Path(persona_base_dir)
    personas = []

    for sub in simple_persona_dir.iterdir():
        if sub.is_dir():
            personas.append(str(sub.absolute()))
    return personas


def get_number_of_conflicts(graph: Graph) -> int:
    '''
    Get the number of conflicts in the graph.
    '''
    return len(list(graph.subjects(RDF.type, NS_DTOU['Conflict'])))


def get_number_of_conflicting_segments(graph: Graph) -> int:
    '''
    Get the number of conflicting segments in the graph.
    '''
    n_conflict = list(graph.subjects(RDF.type, NS_DTOU['Conflict']))
    distinct_segments = set()
    for node in n_conflict:
        text = graph.value(node, NS['text']).toPython()
        distinct_segments.add(text)
    return len(distinct_segments)


async def analyze_personas(personas, practices, max_concurrency=5) -> tuple[dict[str, dict[str, Graph]], dict[str, dict[str, str]]]:
    '''
    Run compliance reasoning over personas and practices.
    This function is async, for running multiple compliance reasoning tasks concurrently.
    Result is a tuple of two dictionaries: conflicts and all_errors.
    The conflicts dictionary has the following structure:
    {
        "persona_dir": {
            "website_name": RDF_GRAPH_OF_CONFLICT_RESULT,
        }
    }
    '''
    conflicts: dict[str, dict[str, Graph]] = {}
    all_errors = {}

    sem_max_personas = Semaphore(3)
    sem_max_jobs = Semaphore(max_concurrency)

    async def analyze_for_persona(persona: str) -> tuple[dict[str, Graph], dict[str, str]]:
        results: dict[str, Graph] = {}
        errors: dict[str, str] = {}

        user_persona_dir = Path(persona)
        subs = list(user_persona_dir.iterdir())
        if not subs:
            print(f"Nothing in user persona at {persona}")
            return

        async def analyze_website(website_choice):
            async with sem_max_jobs:
                res, err = await upa.analyze_pp_with_user_persona(website_choice, website_choice, data_practices=practices[website_choice],
                                                            user_persona_dir=str(user_persona_dir.absolute()))
            if res.serialize().strip():
                results[website_choice] = res
            if err:
                errors[website_choice] = err

        c_analyze = []
        for website_choice in practices.keys():
            c = analyze_website(website_choice)
            c_analyze.append(c)
        for f in tqdm(asyncio.as_completed(c_analyze), total=len(c_analyze), desc=f"Analyzing {user_persona_dir.name}, for websites", leave=False):
            await f

        return results, errors

    async def run_process_for_persona(persona):
        async with sem_max_personas:
            results, errors = await analyze_for_persona(persona)
        persona_name = str(Path(persona).absolute())
        if results:
            conflicts[persona_name] = results
        if errors:
            all_errors[persona_name] = errors

    c_list = []
    for persona in personas:
        c = run_process_for_persona(persona)
        c_list.append(c)
    for f in tqdm(asyncio.as_completed(c_list), total=len(c_list), desc="Looping personas for analysis", leave=True):
        await f

    return conflicts, all_errors


def to_websites_by_num_conflicts(conflicts, websites_of_interest) -> dict[int, list[str]]:
    '''
    Convert the conflicts dictionary to a dictionary of websites by number of conflicts (as key).
    '''
    num_persona_conflicts_per_website = {}
    for ws in websites_of_interest:
        num_persona_conflicts_per_website[ws] = 0
    for persona, results in conflicts.items():
        for ws, res in results.items():
            if ws in websites_of_interest:
                num_persona_conflicts_per_website[ws] += 1

    websites_by_conflicts = defaultdict(list)
    for ws, num_conflicts in num_persona_conflicts_per_website.items():
        websites_by_conflicts[num_conflicts].append(ws)
    websites_by_conflicts = dict(websites_by_conflicts)

    return websites_by_conflicts


def to_personas_by_num_conflicts(conflicts, personas, websites_of_interest=None) -> dict[int, list[str]]:
    '''
    Convert the conflicts dictionary to a dictionary of websites by number of conflicts (as key).
    '''
    num_conflicts_per_persona = {}
    for persona in personas:
        num_conflicts_per_persona[persona] = 0
    for persona, results in conflicts.items():
        num = 0
        for ws, res in results.items():
            if websites_of_interest is None or ws in websites_of_interest:
                num += 1
        num_conflicts_per_persona[persona] = num

    personas_by_conflicts = defaultdict(list)
    for persona, num_conflicts in num_conflicts_per_persona.items():
        if isinstance(persona, Path):
            persona = persona.name
        personas_by_conflicts[num_conflicts].append(persona)
    personas_by_conflicts = dict(personas_by_conflicts)

    return personas_by_conflicts

def websites_with_same_pp(website_list):
    pp_dict = {}
    for ws in website_list:
        p = get_relative_file_path_for_pp(ws)
        content = Path(p).read_text().strip()
        content = content.split('\n', 1)[1]
        if content in pp_dict:
            pp_dict[content].append(ws)
        else:
            pp_dict[content] = [ws]

    res = []
    for pp, ws_list in pp_dict.items():
        if len(ws_list) > 1:
            res.append(ws_list)
    return res
