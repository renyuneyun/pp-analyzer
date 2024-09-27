"""
Main module for the privacy policy analysis.

By default, we assume all segments share the same segmentation method, which is by line breaks.
"""

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
)


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


def analyze_pp(pp_text: str) -> list[DataPractice]:
    """
    Call the relevant LLM tools to analyze the privacy policy.
    This function returns a
    """
    segments = ptu.convert_into_segments(pp_text)

    raw_data_entities = identify_data_entities(pp_text, segments)
    classified_data_entities = classify_data_categories(
        pp_text, segments, raw_data_entities
    )
    raw_purpose_entities = identity_purpose_entities(pp_text, segments)
    classified_purpose_entities = classify_purpose_categories(
        pp_text, segments, raw_purpose_entities
    )
    parties = identify_parties(pp_text, segments)
    practices = identify_data_practices(pp_text, segments)

    grouped_practices = group_data_practices_and_entities(
        practices, classified_data_entities, classified_purpose_entities, parties
    )
    grouped_practices_with_id = add_ids_into_grouped_practices(grouped_practices)

    assembled_data_practice_list = []

    for segment in grouped_practices_with_id:
        query_data = convert_grouped_practices_to_query_data(segment)
        relations = identify_relations(query_data)
        assembled_data_practices = assemble_data_practices(relations, segment)
        assembled_data_practice_list.extend(assembled_data_practices)

    return assembled_data_practice_list
