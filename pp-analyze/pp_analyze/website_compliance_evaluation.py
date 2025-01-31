import asyncio
from asyncio import Semaphore
from collections import defaultdict
from pathlib import Path
from rdflib import Graph, RDF
from tqdm.auto import tqdm
import pp_analyze
from pp_analyze import user_preference_analyze as upa
from pp_analyze.data_model import DataEntity, PurposeEntity, SegmentedDataPractice
from .dtou import NS_DTOU
from .kg import NS
from .pp_analyze import get_relative_file_path_for_pp
from . import policy_text_utils as ptu


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


def get_conflicting_segments(graph: Graph) -> set[str]:
    '''
    Get the number of conflicting segments in the graph.
    If a segment has multiple conflicts, it is counted only once (contrary to above get_number_of_conflicts() which does not take this into account).
    '''
    n_conflict = list(graph.subjects(RDF.type, NS_DTOU['Conflict']))
    distinct_segments = set()
    for node in n_conflict:
        text = graph.value(node, NS['text']).toPython()
        distinct_segments.add(text)
    return distinct_segments


def get_number_of_conflicting_segments(graph: Graph) -> int:
    return len(get_conflicting_segments(graph))


def get_number_of_conflicting_practices(graph: Graph, practices: list[SegmentedDataPractice]) -> int:
    conflicting_segments = get_conflicting_segments(graph)
    num = 0
    for practice in practices:
        if practice.segment in conflicting_segments:
            num += 1
    return num


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
    "Conflict" here means the number of conflicting personal profiles.
    This indicates which websites have the same number of conflicts.
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
    Convert the conflicts dictionary to a dictionary of personas by number of conflicts (as key).
    "Conflict" here means the number of conflicting personal profiles.
    This indicates which persona has the same number of conflicting websites.
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


def get_segment_conflict_info(conflicts, websites_of_interest, practices: dict[str, list[SegmentedDataPractice]]) -> dict[str, tuple[int, int, int, int]]:
    '''
    Compute several information about the number of conflicting profiles to the number of segments.
    Returns a dictionary, key is websites, and value is a tuple of target information:
    - Number of conflicting profiles
    - Number of segments (that create conflicts, sum over all conflict)
    - Number of segments (that create conflicts, distinct)
    - Number of segments (has data practices)
    - Number of data practices
    - Number of segments (in privacy policy)
    - Number of conflicts
    '''
    nums_dict = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])

    for ws in websites_of_interest:
        fp = get_relative_file_path_for_pp(ws)
        n_segments = len(ptu.convert_into_segments(fp.read_text()))
        nums_dict[ws][5] = n_segments
        practice_of_website = practices[ws]
        nums_dict[ws][4] = len(practice_of_website)
        distinct_segments = set()
        for practice in practice_of_website:
            distinct_segments.add(practice.segment)
        nums_dict[ws][3] = len(distinct_segments)

    conflicting_segments_by_ws = {}
    for persona, results in conflicts.items():
        for ws, res in results.items():
            if ws in websites_of_interest:
                nums_dict[ws][0] += 1
                n_segments_conflict = get_number_of_conflicting_segments(res)
                nums_dict[ws][1] += n_segments_conflict
                conflicting_segments = get_conflicting_segments(res)
                if ws not in conflicting_segments_by_ws:
                    conflicting_segments_by_ws[ws] = set()
                conflicting_segments_by_ws[ws].update(conflicting_segments)

                number_of_conflicts = get_number_of_conflicts(res)
                nums_dict[ws][6] += number_of_conflicts

    for ws, segments in conflicting_segments_by_ws.items():
        nums_dict[ws][2] = len(segments)

    return dict(nums_dict)


def calc_average_conflict_rate_by_segment_of_websites(conflicts, websites_of_interest, segment_mode: int = 0, practices: dict[str, list[SegmentedDataPractice]]|None =None) -> dict[int, list[str]]:
    '''
    Calculate the average conflict rate of each website, in terms of the number of conflicting profiles per segment.
    In other words, it is the ratio of the number of conflicting profiles to the number of segments (as the denominator).
    The segment_mode parameter determines how to count the number of segments, as follows:
    - 0: Count the number of all segments in the privacy policy.
    - 1: Count the number of segments that create conflicts (for each profile; if same segment creates multiple conflicting profiles, it is counted multiple times).
        This calculates on average how many conflicting profiles are created per conflicting segment.
    - 2: Same as 1, but do not count the same segment multiple times.
    - 3: Count the number of segments that has data practices (requires `practices` parameter).
        This estimates the average number of conflicting profiles each valid segment creates.
    - 4: Same as 3, but do not count the same segment multiple times.
    - 5: Same as 0, but the numerator is 1 if there is a conflict, 0 otherwise.
    '''
    num_persona_conflicts_per_website = {}
    for ws in websites_of_interest:
        num_persona_conflicts_per_website[ws] = 0
    for persona, results in conflicts.items():
        for ws, res in results.items():
            if ws in websites_of_interest:
                if segment_mode == 5:
                    num_persona_conflicts_per_website[ws] = 1
                else:
                    num_persona_conflicts_per_website[ws] += 1

    ret = {}
    for ws, num_conflicts in num_persona_conflicts_per_website.items():
        if segment_mode == 0 or segment_mode == 5:
            fp = get_relative_file_path_for_pp(ws)
            n_segments = len(ptu.convert_into_segments(fp.read_text()))
        elif segment_mode == 1:
            n_segments = 0
            for persona, results in conflicts.items():
                if ws in results:
                    n_segments += get_number_of_conflicting_segments(results[ws])
        elif segment_mode == 2:
            conflicting_segments = set()
            for persona, results in conflicts.items():
                if ws in results:
                    conflicting_segments.update(get_conflicting_segments(results[ws]))
            n_segments = len(conflicting_segments)
        elif segment_mode == 3:
            practice_of_website = practices[ws]
            n_segments = 0
            for practice in practice_of_website:
                n_segments += 1
        elif segment_mode == 4:
            practice_of_website = practices[ws]
            valid_segments = set()
            for practice in practice_of_website:
                valid_segments.add(practice.segment)
            n_segments = len(valid_segments)
        else:
            raise ValueError("Invalid segment_mode")
        if num_conflicts == 0:
            ret[ws] = 0
        else:
            ret[ws] = num_conflicts / n_segments

    return ret


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
