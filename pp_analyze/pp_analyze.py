"""
Main module for the privacy policy analysis.

By default, we assume all segments share the same segmentation method, which is by line breaks.
"""

from dotenv import load_dotenv
import os
from pathlib import Path
import re
from tqdm import tqdm
from . import policy_text_utils as ptu
from .data_model import (
    DataEntity,
    PurposeEntity,
    PartyEntity,
    DataPractice,
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


def assemble_data_practices(relations: list[Relation], grouped_practices_with_id: SWGroupedDataPracticeWithId) -> list[DataPractice]:
    """
    Assemble the data practices with the identified relations, into DataPractice objects.

    @param relations: identified relations, obtained from identify_relations
    @param grouped_practices_with_id: list of grouped data practices with IDs, obtained from add_ids_into_grouped_practices, but only the segment relevant to the relations
    @return: list of DataPractice objects
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
    for action_id, my_relations in indexed_relations.items():
        raw_action = indexed_practices[action_id]
        assert raw_action["type"] in DATA_PRACTICE_NAME_MAP, f"Unexpected data practice type: {raw_action['type']}"
        cls = DATA_PRACTICE_CLASS_MAP[DATA_PRACTICE_NAME_MAP[raw_action["type"]]]
        obj = cls(text=raw_action["text"], **my_relations)
        res.append(obj)
    return res


def analyze_pp(pp_text: str, override_cache: PARAM_OVERRIDE_CACHE = None) -> list[DataPractice]:
    """
    Main entry point for pp_analyze.
    Call the relevant LLM tools to analyze the privacy policy.
    This function returns a list of DataPractice objects.
    """
    segments = ptu.convert_into_segments(pp_text)

    raw_data_entities = identify_data_entities(pp_text, segments, override_cache)
    classified_data_entities = classify_data_categories(
        pp_text, segments, raw_data_entities, override_cache
    )
    raw_purpose_entities = identity_purpose_entities(pp_text, segments, override_cache)
    classified_purpose_entities = classify_purpose_categories(
        pp_text, segments, raw_purpose_entities, override_cache
    )
    parties = identify_parties(pp_text, segments, override_cache)
    practices = identify_data_practices(pp_text, segments, override_cache)

    grouped_practices = group_data_practices_and_entities(
        practices, classified_data_entities, classified_purpose_entities, parties
    )
    grouped_practices_with_id = add_ids_into_grouped_practices(grouped_practices)

    assembled_data_practice_list = []

    for segment in grouped_practices_with_id:
        query_data = convert_grouped_practices_to_query_data(segment)
        relations = identify_relations(query_data, override_cache)
        assembled_data_practices = assemble_data_practices(relations, segment)
        assembled_data_practice_list.extend(assembled_data_practices)

    return assembled_data_practice_list


RE_DOMAIN_NAME = re.compile(r"(?:https?://)?([^/]+)")
RE_KEY_DOMAIN_NAME = re.compile(r"(?:https?://)?www\.([^/]+)")


def get_relative_file_path_for_pp(website_name: str) -> Path:
    policy_dir = os.getenv("PP_POLICY_DIR")
    if policy_dir is None:
        raise ValueError("PP_POLICY_DIR environment variable is not set.")
    policy_dir = Path(policy_dir)
    return policy_dir / website_name[:1] / website_name[:2] / website_name[:3] / f"{website_name}.md"


def analyze_pp_from_names(website_names: list[str], override_cache: PARAM_OVERRIDE_CACHE = None):
    """
    Analyze privacy policies from website names.
    You need `PP_POLICY_DIR` environment variable to be set to the directory containing the privacy policies.
    """
    policy_dir = os.getenv("PP_POLICY_DIR")
    if policy_dir is None:
        raise ValueError("PP_POLICY_DIR environment variable is not set.")
    policy_dir = Path(policy_dir)
    res = {}
    errs = []
    for website_name in tqdm(website_names, desc="Analyzing privacy policy for website #"):
        possbile_names = []
        if match := RE_KEY_DOMAIN_NAME.match(website_name):
            domain_name = match.group(1)
            possbile_names.append(domain_name)
        if match := RE_DOMAIN_NAME.match(website_name):
            domain_name = match.group(1)
            possbile_names.append(domain_name)
        match_found = False
        for domain_name in possbile_names:
            pp_file = get_relative_file_path_for_pp(domain_name)
            if not pp_file.exists():
                continue
            print(f"Analyzing privacy policy for {website_name} from {pp_file}")
            with open(pp_file, "r") as f:
                pp_text = f.read()
                data_practices = analyze_pp(pp_text, override_cache=override_cache)
                print(f"Data practices for {domain_name}: {data_practices}")
                res[domain_name] = data_practices
                match_found = True
                break
        if not match_found:
            errs.append(website_name)
    return res, errs
