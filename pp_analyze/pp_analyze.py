"""
Main module for the privacy policy analysis.

By default, we assume all segments share the same segmentation method, which is by line breaks.
"""

from copy import deepcopy
from logging import Logger
from typing import Generic, TypeVar, Type
from pydantic import BaseModel
# from pydantic.generics import GenericModel
from . import policy_text_utils as ptu
from .data_model import (
    DataEntity,
    PurposeEntity,
    PartyEntity,
    DataPractice,
    DataCollectionUse,
    DataSharingDisclosure,
    DataStorageRetention,
    DataSecurityProtection,
    K_DATA_PRACTICE_DATA_COLLECTION_USE,
    K_DATA_PRACTICE_DATA_SHARING_DISCLOSURE,
    K_DATA_PRACTICE_DATA_STORAGE_RETENTION,
    K_DATA_PRACTICE_DATA_SECURITY_PROTECTION,
    DATA_PRACTICE_NAME_MAP,
    DATA_PRACTICE_CLASS_MAP,
)
from .query_helper import (
    Q_DATA_ENTITY,
    Q_DATA_CLASSIFICATION,
    Q_ACTION_RECOGNITION,
    Q_RELATION_RECOGNITION,
)


log = Logger(__name__)


def to_dict(obj_or_list: list[BaseModel] | BaseModel) -> dict | list[dict]:
    if isinstance(obj_or_list, list):
        return [to_dict(x) for x in obj_or_list]
    return obj_or_list.model_dump()


class _BaseModel(BaseModel):
    class Config:
        frozen = True


T = TypeVar('T')


class IEntity(_BaseModel):
    text: str
    span: tuple[int, int]


class ClassifiedEntity(IEntity):
    category: str


class SWEntities(_BaseModel, Generic[T]):
    segment: str
    entities: list[T]


IDataEntity = IEntity
IPurposeEntity = IEntity
ClassifiedDataEntity = ClassifiedEntity
ClassifiedPurposeEntity = ClassifiedEntity

SWDataEntities = SWEntities[IDataEntity]
SWClassifiedDataEntities = SWEntities[ClassifiedDataEntity]
SWPurposeEntities = SWEntities[IPurposeEntity]
SWClassifiedPurposeEntities = SWEntities[ClassifiedPurposeEntity]


class IDataPractice(_BaseModel):
    type: str
    text: str
    span: tuple[int, int]


class SWDataPractices(_BaseModel):

    segment: str
    practices: list[IDataPractice]


def identify_data_entities(pp_text: str, segments: list[str]) -> list[SWDataEntities]:
    """
    Split pp_text into segments, and call LLM to obtain data entities
    Takes privacy policy (segment or any other form) as input
    Return results in the following form:
    [
        {
            'segment': SEGMENT_TEXT,
            'entities': [
                {
                    'text': ENTITY_TEXT,
                    'span': (START, END)
                }
            ]
        }
    ]
    """
    def call_llm_for_segment(segment_text):
        parsed_model_output = Q_DATA_ENTITY.run_query({"segment": segment_text})
        res = []
        for entity in parsed_model_output:
            entity_text = None
            if isinstance(entity, str):
                entity_text = entity
            elif isinstance(entity, dict):
                entity_text = entity['text']
            else:
                raise ValueError(f"Unexpected entity type: {type(entity)}")
            start_pos = segment_text.find(entity_text)
            end_pos = start_pos + len(entity_text)
            span = (start_pos, end_pos)
            res.append({"text": entity_text, "span": span})
        return res

    log.info("Identifying data entities")

    res = []
    for segment in segments:
        entities = call_llm_for_segment(segment)
        res.append(SWDataEntities(**{"segment": segment, "entities": entities}))
    return res


def classify_data_categories(pp_text: str, segments: list[str], data_entities: list[SWDataEntities]) -> list[SWClassifiedDataEntities]:
    """
    Identify the formal categories of data entities, as in DPV

    @param segments: list of pp segments, obtained from, e.g., convert_into_segments
    @param data_entities: list of data entities, obtained from identify_data_entities
    @return: list of data entities with categories, in the following form (of type SegmentWithClassifiedEntitiesList):
    [
        {
            'segment': SEGMENT_TEXT,
            'entities': [
                {
                    'text': ENTITY_TEXT,
                    'span': (START, END),
                    'category': CATEGORY_URI
                }
            ]
        }
    ]
    """
    def call_llm_for_data_point(data_point):
        return Q_DATA_CLASSIFICATION.run_query({
            'segment': data_point['segment'],
            'phrases': [entity['text'] for entity in data_point['entities']]
        })

    log.info("Classifying data categories")

    classified_data_entities = []
    for x in deepcopy(data_entities):
        x_dict = to_dict(x)
        categories = call_llm_for_data_point(x_dict)
        classified_entities = []
        for i, entity in enumerate(x_dict["entities"]):
            classified_entity = ClassifiedDataEntity({
                "category": categories[i],
                **entity
            })
            classified_entities.append(classified_entity)
        x_dict.update({"entities": classified_entities})
        classified_data_entities.append(SWClassifiedDataEntities(**x_dict))
    return classified_data_entities


def identity_purpose_entities(pp_text: str, segments: list[str]):
    """
    Split pp_text into segments, and call LLM to obtain purpose entities
    Takes privacy policy (segment or any other form) as input
    Return results in the following form:
    [
        {
            'segment': SEGMENT_TEXT,
            'entities': [
                {
                    'text': ENTITY_TEXT,
                    'span': (START, END)
                }
            ]
        }
    ]
    """

    def call_llm_for_segment(segment_text):
        pass

    res = []
    for segment in segments:
        entities = call_llm_for_segment(segment)
        res.append({"segment": segment, "entities": entities})
    return res


def classify_purpose_categories(pp_text: str, segments: list[str], purpose_entities):
    """
    Identify the formal categories of purpose entities, as in DPV

    @param pp_text: privacy policy text
    @param purpose_entities: list of purpose entities, obtained from identify_purpose_entities
    @return: list of purpose entities with categories, in the following form:
    [
        {
            'segment': SEGMENT_TEXT,
            'entities': [
                {
                    'text': ENTITY_TEXT,
                    'span': (START, END),
                    'category': CATEGORY_URI
                }
            ]
        }
    ]
    """

    def call_llm_for_data_point(data_point):
        pass

    purpose_entities = deepcopy(purpose_entities)
    for x in purpose_entities:
        categories = call_llm_for_data_point(x)
        for i, entity in enumerate(x["entities"]):
            entity["category"] = categories[i]
    return purpose_entities


def identify_parties(pp_text: str, segments: list[str]):
    """
    Identify the parties involved in the privacy policy

    @param pp_text: privacy policy text
    @return: list of parties, in the following form:
    [
        {
            'segment': SEGMENT_TEXT,
            'parties': [
                {
                    'text': PARTY_TEXT,
                    'span': (START, END),
                    'category': PARTY_CATEGORY
                }
            ]
        }
    ]
    """


def identify_data_storage_locations(pp_text: str, segments: list[str]):
    # TODO: Not implemented yet!!!
    pass


def identify_data_storage_durations(pp_text: str, segments: list[str]):
    # TODO: Not implemented yet!!!
    pass


def identify_data_practices(pp_text: str, segments: list[str]) -> list[SWDataPractices]:
    """
    Identify data practices in the privacy policy

    @param pp_text: privacy policy text
    @return: list of data practices, in the following form:
    [
        {
            'segment': SEGMENT_TEXT,
            'practices': [
                {
                    'type': PRACTICE_TYPE,
                    'text': PRACTICE_TEXT,
                    'span': (START, END)
                }
            ]
        }
    ]
    """
    def call_llm_for_segment(segment_text):
        parsed_model_output = Q_ACTION_RECOGNITION.run_query({"segment": segment_text})
        res = []
        for segment_action in parsed_model_output:
            practice = {
                "type": segment_action["action_type"],
                "text": segment_action["text"],
            }
            start_pos = segment_text.find(segment_action["text"])
            end_pos = start_pos + len(segment_action["text"])
            practice["span"] = (start_pos, end_pos)
            res.append(practice)
        return res

    log.info("Identifying data practices")

    res = []
    for segment in segments:
        practices = call_llm_for_segment(segment)
        res.append(SWDataPractices(**{"segment": segment, "practices": practices}))
    return res


def identify_relations(relation_query):
    """
    Identify relations between data practice actions and entities in the privacy policy, through LLM

    @param relation_query: a query data for the LLM, which are elements from convert_grouped_practices_to_query_data
    @return: list of identified relations, in the following form:
    [
        {
            "action_id": ACTION_ID,
            "entity_id": ENTITY_ID,
            "relation": RELATION_TYPE
        }
    ]
    """
    log.info("Identifying relations")

    return Q_RELATION_RECOGNITION.run_query(relation_query)


def group_data_practices_and_entities(
    data_practices: list[SWDataPractices], classified_data_entities: list[SWClassifiedDataEntities], classified_purpose_entities, parties
):
    """
    Group relevant information into the data practices.

    @param data_practices: list of data practices, obtained from identify_data_practices
    @param classified_data_entities: list of data entities with categories, obtained from classify_data_categories
    @param classified_purpose_entities: list of purpose entities with categories, obtained from classify_purpose_categories
    @param parties: list of parties, obtained from identify_parties
    @return: list of data practices with relevant information, in the following form:
    [
        {
            'segment': SEGMENT_TEXT,
            'practices': [
                {
                    'type': PRACTICE_TYPE,
                    'text': PRACTICE_TEXT,
                    'span': (START, END),
                    'parties': [PARTY_ENTITY],
                    'data': [DATA_ENTITY],
                    'purpose': [PURPOSE_ENTITY]
                }
            ]
        }
    ]
    """
    indexed_data_entities = {
        segment["segment"]: segment["entities"] if "entities" in segment else []
        for segment in to_dict(classified_data_entities)
    }
    indexed_purpose_entities = {
        segment["segment"]: segment["entities"] if "entities" in segment else []
        for segment in classified_purpose_entities
    }
    indexed_parties = {
        segment["segment"]: segment["entities"] if "entities" in segment else []
        for segment in parties
    }

    res = []

    for isegment in data_practices:
        segment = to_dict(isegment)
        segment_text = segment["segment"]
        practices = segment["practices"]
        practice_parties = indexed_parties[segment_text] if segment_text in indexed_parties else []
        practice_data = indexed_data_entities[segment_text] if segment_text in indexed_data_entities else []
        practice_purpose = indexed_purpose_entities[segment_text] if segment_text in indexed_purpose_entities else []
        res.append(
            {
                "segment": segment_text,
                "practices": [
                    {
                        **practice,
                        "parties": [
                            party
                            for party in practice_parties
                            # if party["span"][0] >= practice["span"][0]
                            # and party["span"][1] <= practice["span"][1]
                        ],
                        "data": [
                            data
                            for data in practice_data
                            # if data["span"][0] >= practice["span"][0]
                            # and data["span"][1] <= practice["span"][1]
                        ],
                        "purpose": [
                            purpose
                            for purpose in practice_purpose
                            # if purpose["span"][0] >= practice["span"][0]
                            # and purpose["span"][1] <= practice["span"][1]
                        ],
                    }
                    for practice in practices
                ],
            }
        )
    return res


def add_ids_into_grouped_practices(grouped_practices):
    """
    Add IDs into the grouped practices, for both practices and entities.
    The ID is simply the index of the data practice or entity in the list, and only serves the purpose of internal identification.
    Note that IDs are grouped by segments, so the same ID may appear in different segments.

    @param grouped_practices: list of grouped data practices, obtained from group_data_practices_and_entities
    @return: list of grouped data practices with IDs, in the following form:
    [
        {
            'segment': SEGMENT_TEXT,
            'practices': [
                {
                    'id': PRACTICE_ID,
                    'type': PRACTICE_TYPE,
                    'text': PRACTICE_TEXT,
                    'span': (START, END),
                    'parties': [
                        {
                            'id': ENTITY_ID,
                            'text': PARTY_TEXT,
                            'span': (START, END),
                            'category': PARTY_CATEGORY
                        }
                    ],
                    'data': [
                        {
                            'id': ENTITY_ID,
                            'text': DATA_TEXT,
                            'span': (START, END),
                            'category': DATA_CATEGORY
                        }
                    ],
                    'purpose': [
                        {
                            'id': ENTITY_ID,
                            'text': PURPOSE_TEXT,
                            'span': (START, END),
                            'category': PURPOSE_CATEGORY
                        }
                    ]
                }
            ]
        }
    ]
    """
    res = deepcopy(grouped_practices)
    for segment in res:
        segment_text = segment["segment"]
        entity_counter = 0
        practices = segment["practices"]
        for practice_index, practice in enumerate(practices):
            practice["id"] = f"C{practice_index+1}"
            for party in practice["parties"]:
                entity_counter += 1
                party["id"] = f"D{entity_counter}"
            for data in practice["data"]:
                entity_counter += 1
                data["id"] = f"D{entity_counter}"
            for purpose in practice["purpose"]:
                entity_counter += 1
                purpose["id"] = f"D{entity_counter}"
    return res


def convert_grouped_practices_to_query_data(grouped_practices_with_id):
    """
    Convert grouped practices to query data for the LLM.

    @param grouped_practices_with_id: a grouped data practices, which is an element obtained from add_ids_into_grouped_practices
    @return: list of query data for the LLM, in the following form:
    {
        'segment': SEGMENT_TEXT,
        'targets': {
            'action_contexts': [
                {
                    'id': DATA_PRACTICE_ID,
                    'action_type': DATA_PRACTICE_TYPE,
                    'text': DATA_PRACTICE_TEXT
                }
            ],
            'entities': [
                {
                    'id': ENTITY_ID,
                    'text': ENTITY_TEXT,
                    'type': ENTITY_TYPE
                }
            ]
        }
    }
    """
    segment = grouped_practices_with_id
    segment_text = segment["segment"]
    practices = segment["practices"]
    action_contexts = [
        {
            "id": practice["id"],
            "action_type": practice["type"],
            "text": practice["text"],
        }
        for practice in practices
    ]
    entities = []
    for practice in practices:
        for entity in practice["data"]:
            entity_info = {"id": entity["id"], "text": entity["text"], "type": "Data"}
            entities.append(entity_info)
        for entity in practice["purpose"]:
            entity_info = {
                "id": entity["id"],
                "text": entity["text"],
                "type": "Purpose",
            }
            entities.append(entity_info)
        for entity in practice["parties"]:
            entity_info = {
                "id": entity["id"],
                "text": entity["text"],
                "type": entity["category"],
            }
            entities.append(entity_info)
    res = {
        "segment": segment_text,
        "targets": {"action_contexts": action_contexts, "entities": entities},
    }
    return res


def assemble_data_practices(relations, grouped_practices_with_id):
    """
    Assemble the data practices with the identified relations, into DataPractice objects.

    @param relations: identified relations, obtained from identify_relations
    @param grouped_practices_with_id: list of grouped data practices with IDs, obtained from add_ids_into_grouped_practices, but only the segment relevant to the relations
    @return: list of DataPractice objects
    """
    grouped_practices_with_id = deepcopy(grouped_practices_with_id)
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
            obj = PartyEntity(text=entity["text"], category=entity["category"])
            indexed_entity_objs[entity["id"]] = obj

    indexed_relations = {}
    for relation in relations:
        action_id = relation["action_id"]
        entity_id = relation["entity_id"]
        relation_type = relation["relation"]
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
    # raw_purpose_entities = identity_purpose_entities(pp_text, segments)
    # classified_purpose_entities = classify_purpose_categories(
    #     pp_text, segments, raw_purpose_entities
    # )
    classified_purpose_entities = []
    # parties = identify_parties(pp_text, segments)
    parties = []
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
