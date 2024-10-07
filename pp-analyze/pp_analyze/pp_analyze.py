"""
Main module for the privacy policy analysis.

By default, we assume all segments share the same segmentation method, which is by line breaks.
"""

import asyncio
from dotenv import load_dotenv
from enum import Enum
import os
from pathlib import Path
from pydantic import BaseModel, ValidationError
import re
from tqdm.auto import tqdm
from . import policy_text_utils as ptu
from .data_model import (
    DataEntity,
    PurposeEntity,
    PartyEntity,
    SegmentedDataPractice,
    DATA_PRACTICE_NAME_MAP,
    DATA_PRACTICE_CLASS_MAP,
)
from .recognition import (
    identify_data_entities,
    classify_data_categories,
    identity_purpose_entities,
    classify_purpose_categories,
    identify_parties,
    identify_data_practices,
    group_data_practices_and_entities,
    add_ids_into_grouped_practices,
    convert_grouped_practices_to_query_data,
    identify_relations,

    to_dict,
    SWGroupedDataPracticeWithId,
    Relation,

    QueryCategory,
    PARAM_OVERRIDE_CACHE,
)


load_dotenv()


def assemble_data_practices(relations: list[Relation], grouped_practices_with_id: SWGroupedDataPracticeWithId) -> tuple[SegmentedDataPractice, list[str]]:
    """
    Assemble the data practices with the identified relations, into DataPractice objects. The results denote each segment of the privacy policy with the relevant data practices.

    @param relations: identified relations, obtained from identify_relations
    @param grouped_practices_with_id: list of grouped data practices with IDs, obtained from add_ids_into_grouped_practices, but only the segment relevant to the relations
    @return: SegmentedDataPractice object, which contains the segment text and the assembled data practices
    """
    grouped_practices_with_id = to_dict(grouped_practices_with_id)
    segment_text = grouped_practices_with_id["segment"]
    practices = grouped_practices_with_id["practices"]
    indexed_practices = {}
    indexed_entity_objs = {}
    for practice in practices:
        indexed_practices[practice["id"]] = practice

    for practice in practices:
        for entity in practice["data"]:
            obj = DataEntity(text=entity["text"], category=entity["category"])
            indexed_entity_objs[entity["id"]] = obj
        for entity in practice["purpose"]:
            obj = PurposeEntity(text=entity["text"], category=entity["category"])
            indexed_entity_objs[entity["id"]] = obj
        for entity in practice["parties"]:
            obj = PartyEntity(text=entity["text"], category=entity["party_type"])
            indexed_entity_objs[entity["id"]] = obj

    indexed_relations = {}
    for relation in relations:
        action_id = relation.action_id
        entity_id = relation.entity_id
        relation_type = relation.relation
        if action_id not in indexed_relations:
            indexed_relations[action_id] = {}
        if relation_type not in indexed_relations[action_id]:
            indexed_relations[action_id][relation_type] = []
        indexed_relations[action_id][relation_type].append(indexed_entity_objs[entity_id])

    res = []
    errors = []
    for action_id, my_relations in indexed_relations.items():
        raw_action = indexed_practices[action_id]
        if raw_action["type"] not in DATA_PRACTICE_NAME_MAP:
            errors.append(f"Unexpected data practice type for {raw_action}")
            continue
        cls = DATA_PRACTICE_CLASS_MAP[DATA_PRACTICE_NAME_MAP[raw_action["type"]]]
        try:
            obj = cls(text=raw_action["text"], **my_relations)
        except ValidationError as e:
            errors.append(f"Validation error for {raw_action}: {e}")
            continue
        res.append(obj)
    segmented_data_practice = SegmentedDataPractice(segment=segment_text, practices=res)
    return segmented_data_practice, errors


class PPAnalyzeStep(Enum):
    IDENTIFY_DATA_ENTITIES = "Identify data entities"
    CLASSIFY_DATA_ENTITIES = "Classify data entities"
    IDENTIFY_PURPOSE_ENTITIES = "Identify purpose entities"
    CLASSIFY_PURPOSE_ENTITIES = "Classify purpose entities"
    IDENTIFY_PARTIES = "Identify parties"
    IDENTIFY_DATA_PRACTICES = "Identify data practices"
    GROUP_DATA_PRACTICES = "Group data practices"
    ADD_IDS = "Add IDs"
    IDENTIFY_RELATIONS = "Identify relations"
    ASSEMBLE_DATA_PRACTICES = "Assemble data practices"


async def analyze_pp(pp_text: str, override_cache: PARAM_OVERRIDE_CACHE = None, batch: bool = False) -> tuple[list[SegmentedDataPractice], list[BaseModel|str]]:
    """
    Main entry point for pp_analyze.
    Call the relevant LLM tools to analyze the privacy policy.
    This function returns a list of DataPractice objects.
    """
    assembled_data_practice_list: list[SegmentedDataPractice] = []
    failed_tasks: list[BaseModel|str] = []
    pending_steps = []
    with tqdm(total=len(PPAnalyzeStep.__members__), leave=False, desc="Analyzing privacy policy") as pbar:
        def add_step(step):
            pending_steps.append(step)
            pbar.set_postfix_str(str(pending_steps))
        def resolve_step(finished_step):
            pending_steps.remove(finished_step)
            pbar.update(1)
            pbar.set_postfix_str(str(pending_steps))

        segments = ptu.convert_into_segments(pp_text)

        async def get_classified_data_entities():
            add_step(PPAnalyzeStep.IDENTIFY_DATA_ENTITIES)
            raw_data_entities = await identify_data_entities(pp_text, segments, override_cache, batch=batch)
            resolve_step(PPAnalyzeStep.IDENTIFY_DATA_ENTITIES)
            add_step(PPAnalyzeStep.CLASSIFY_DATA_ENTITIES)
            classified_data_entities, errs = await classify_data_categories(
                pp_text, segments, raw_data_entities, override_cache, batch=batch
            )
            if errs:
                failed_tasks.append(errs)
            resolve_step(PPAnalyzeStep.CLASSIFY_DATA_ENTITIES)
            return classified_data_entities

        t_classified_data_entities = get_classified_data_entities()

        async def get_classified_purpose_entities():
            add_step(PPAnalyzeStep.IDENTIFY_PURPOSE_ENTITIES)
            raw_purpose_entities = await identity_purpose_entities(pp_text, segments, override_cache, batch=batch)
            resolve_step(PPAnalyzeStep.IDENTIFY_PURPOSE_ENTITIES)
            add_step(PPAnalyzeStep.CLASSIFY_PURPOSE_ENTITIES)
            classified_purpose_entities, errs = await classify_purpose_categories(
                pp_text, segments, raw_purpose_entities, override_cache, batch=batch
            )
            if errs:
                failed_tasks.append(errs)
            resolve_step(PPAnalyzeStep.CLASSIFY_PURPOSE_ENTITIES)
            return classified_purpose_entities

        t_classified_purpose_entities = get_classified_purpose_entities()

        async def get_parties():
            add_step(PPAnalyzeStep.IDENTIFY_PARTIES)
            parties = await identify_parties(pp_text, segments, override_cache, batch=batch)
            resolve_step(PPAnalyzeStep.IDENTIFY_PARTIES)
            return parties

        t_parties = get_parties()

        async def get_practices():
            add_step(PPAnalyzeStep.IDENTIFY_DATA_PRACTICES)
            practices = await identify_data_practices(pp_text, segments, override_cache, batch=batch)
            resolve_step(PPAnalyzeStep.IDENTIFY_DATA_PRACTICES)
            return practices

        t_practices = get_practices()

        classified_data_entities, classified_purpose_entities, parties, practices = await asyncio.gather(
            t_classified_data_entities, t_classified_purpose_entities, t_parties, t_practices
        )

        add_step(PPAnalyzeStep.GROUP_DATA_PRACTICES)
        grouped_practices = group_data_practices_and_entities(
            practices, classified_data_entities, classified_purpose_entities, parties
        )
        resolve_step(PPAnalyzeStep.GROUP_DATA_PRACTICES)
        add_step(PPAnalyzeStep.ADD_IDS)
        grouped_practices_with_id = add_ids_into_grouped_practices(grouped_practices)
        resolve_step(PPAnalyzeStep.ADD_IDS)

        async def get_relations():
            add_step(PPAnalyzeStep.IDENTIFY_RELATIONS)
            relation_queries = []
            for segment in tqdm(grouped_practices_with_id, desc='Combining data practices into relation queries', leave=False):
                query_data = convert_grouped_practices_to_query_data(segment)
                relation_queries.append(query_data)

            relations = await identify_relations(relation_queries, override_cache, batch=batch)
            assert len(relations) == len(grouped_practices_with_id), "Mismatch in relation count"
            resolve_step(PPAnalyzeStep.IDENTIFY_RELATIONS)
            return relations

        relations = await get_relations()

        add_step(PPAnalyzeStep.ASSEMBLE_DATA_PRACTICES)
        for i_relations, segment in tqdm(zip(relations, grouped_practices_with_id), desc='Assembling data practices', leave=False):
            assembled_data_practices, errs = assemble_data_practices(i_relations, segment)
            if errs:
                failed_tasks.extend(errs)
            assembled_data_practice_list.append(assembled_data_practices)
        resolve_step(PPAnalyzeStep.ASSEMBLE_DATA_PRACTICES)

    return assembled_data_practice_list, failed_tasks


RE_DOMAIN_NAME = re.compile(r"(?:https?://)?([^/]+)")
RE_KEY_DOMAIN_NAME = re.compile(r"(?:https?://)?www\.([^/]+)")


def get_relative_file_path_for_pp(website_name: str) -> Path:
    policy_dir = os.getenv("PP_POLICY_DIR")
    if policy_dir is None:
        raise ValueError("PP_POLICY_DIR environment variable is not set.")
    policy_dir = Path(policy_dir)
    return policy_dir / website_name[:1] / website_name[:2] / website_name[:3] / f"{website_name}.md"


async def analyze_pp_from_website_name(website_name: str, override_cache: PARAM_OVERRIDE_CACHE = None, only_non_empty: bool = True, batch: bool = False):
    data_practices = None
    errs = []

    possbile_names = []
    if match := RE_KEY_DOMAIN_NAME.match(website_name):
        domain_name = match.group(1)
        possbile_names.append(domain_name)
    if match := RE_DOMAIN_NAME.match(website_name):
        domain_name = match.group(1)
        possbile_names.append(domain_name)
    for domain_name in (pbar := tqdm(possbile_names, leave=False, desc="Using domain name")):
        pbar.set_postfix_str(f"Trying {domain_name}")
        pp_file = get_relative_file_path_for_pp(domain_name)
        if not pp_file.exists():
            continue
        with open(pp_file, "r") as f:
            pp_text = f.read()
            data_practices, errs = await analyze_pp(pp_text, override_cache=override_cache, batch=batch)
            if only_non_empty:
                data_practices = filter_empty_data_practices(data_practices)
            pbar.container.close()
            break
    return data_practices, errs


async def bulk_analyze_pp(website_names: list[str], override_cache: PARAM_OVERRIDE_CACHE = None, only_non_empty: bool = True, batch: bool = False, max_num: int|None = None):
    """
    Analyze privacy policies from website names.
    You need `PP_POLICY_DIR` environment variable to be set to the directory containing the privacy policies.
    """
    res: dict[str, list[SegmentedDataPractice]] = {}
    failed_tasks = []
    errs = []
    if max_num
        desc_str = f"Running bulk privacy policy analysis (max: {max_num})"
    else:
        desc_str = "Running bulk privacy policy analysis"
    for website_name in (pbar := tqdm(website_names, leave=False, desc=desc_str)):
        pbar.set_postfix_str(f"For {website_name}")
        data_practices, ierrs = await analyze_pp_from_website_name(website_name, override_cache=override_cache, only_non_empty=only_non_empty, batch=batch)
        if ierrs:
            errs.append((website_name, ierrs))
        if data_practices is None:
            failed_tasks.append(website_name)
        else:
            res[website_name] = data_practices
            if max_num:
                pbar.set_description_str(f"Running bulk privacy policy analysis (max: {max_num}, {len(res)} found)")
        if max_num and len(res) >= max_num:
            break
    return res, failed_tasks, errs


def filter_empty_data_practices(data_practices: list[SegmentedDataPractice]) -> list[SegmentedDataPractice]:
    return [segmented_data_practice for segmented_data_practice in data_practices if segmented_data_practice.practices]
