from copy import deepcopy
from tqdm.auto import tqdm
from . import query_helper as qh
from .types import PARAM_OVERRIDE_CACHE
from .data_model import (
    to_dict,
    SWDataEntities,
    SWClassifiedDataEntities,
    SWPurposeEntities,
    SWClassifiedPurposeEntities,
    SWPartyEntities,
    SWDataPractices,
    ClassifiedDataEntity,
    ClassifiedPurposeEntity,
    Relation,
)
from ..hierarchy_helper import map_purpose_to_level, map_data_category_to_level


S_DATA_CATEGORY_GENERAL = 'Data-general'
S_PURPOSE_CATEGORY_GENERAL = 'Purpose-general'


PURPOSE_MAPPING_LEVEL = 1
DATA_CATEGORY_MAPPING_LEVEL = 1


def identify_data_entities(pp_text: str, segments: list[str], override_cache: PARAM_OVERRIDE_CACHE = None) -> list[SWDataEntities]:
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
        parsed_model_output = qh.Q_DATA_ENTITY.run_query({"segment": segment_text}, override_cache=override_cache)
        res = []
        for entity in parsed_model_output:
            entity_text = entity
            start_pos = segment_text.find(entity_text)
            end_pos = start_pos + len(entity_text)
            span = (start_pos, end_pos)
            res.append({"text": entity_text, "span": span})
        return res

    res = []
    for segment in tqdm(segments, leave=False, desc="Identifying data entities"):
        entities = call_llm_for_segment(segment)
        res.append(SWDataEntities(**{"segment": segment, "entities": entities}))
    return res


def classify_data_categories(pp_text: str, segments: list[str], data_entities: list[SWDataEntities], override_cache: PARAM_OVERRIDE_CACHE = None, handle_incorrect_llm = True) -> list[SWClassifiedDataEntities]:
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
        return qh.Q_DATA_CLASSIFICATION.run_query({
            'segment': data_point['segment'],
            'phrases': [entity['text'] for entity in data_point['entities']]
        }, override_cache=override_cache)

    classified_data_entities = []
    errs = []
    for x in tqdm(deepcopy(data_entities), leave=False, desc="Classifying data entities"):
        x_dict = to_dict(x)
        categories = call_llm_for_data_point(x_dict)
        classified_entities = []
        if len(categories) != len(x_dict["entities"]):
            errs.append(x)
            if handle_incorrect_llm:
                categories = [S_DATA_CATEGORY_GENERAL] * len(x_dict["entities"])
            else:
                raise ValueError("The number of categories does not match the number of entities")
        for i, entity in enumerate(x_dict["entities"]):
            classified_entity = ClassifiedDataEntity(**{
                "category": map_data_category_to_level(categories[i], level=DATA_CATEGORY_MAPPING_LEVEL),
                **entity
            })
            classified_entities.append(classified_entity)
        x_dict.update({"entities": classified_entities})
        classified_data_entities.append(SWClassifiedDataEntities(**x_dict))
    return classified_data_entities, errs


def identity_purpose_entities(pp_text: str, segments: list[str], override_cache: PARAM_OVERRIDE_CACHE = None) -> list[SWPurposeEntities]:
    """
    Split pp_text into segments, and call LLM to obtain purpose entities
    Takes privacy policy (segment or any other form) as input
    Return results in the following form (as a list of SegmentWithEntitiesList):
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
        parsed_model_output = qh.Q_PURPOSE_ENTITY.run_query({"segment": segment_text}, override_cache=override_cache)
        res = []
        for entity in parsed_model_output:
            entity_text = entity
            start_pos = segment_text.find(entity_text)
            end_pos = start_pos + len(entity_text)
            span = (start_pos, end_pos)
            res.append({"text": entity_text, "span": span})
        return res

    res = []
    for segment in tqdm(segments, leave=False, desc="Identifying purpose entities"):
        entities = call_llm_for_segment(segment)
        res.append(SWPurposeEntities(**{"segment": segment, "entities": entities}))
    return res


def classify_purpose_categories(pp_text: str, segments: list[str], purpose_entities: list[SWPurposeEntities], override_cache: PARAM_OVERRIDE_CACHE = None, handle_incorrect_llm = True) -> list[SWClassifiedPurposeEntities]:
    """
    Identify the formal categories of purpose entities, as in DPV

    @param pp_text: privacy policy text
    @param purpose_entities: list of purpose entities, obtained from identify_purpose_entities
    @return: list of purpose entities with categories, in the following form (as a list of SegmentWithClassifiedEntitiesList):
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
        return qh.Q_PURPOSE_CLASSIFICATION.run_query({
            'segment': data_point['segment'],
            'phrases': [entity['text'] for entity in data_point['entities']]
        }, override_cache=override_cache)

    purpose_entities = deepcopy(purpose_entities)
    classified_purpose_entities = []
    errs = []
    for x in tqdm(purpose_entities, leave=False, desc="Classifying purpose entities"):
        x_dict = to_dict(x)
        categories = call_llm_for_data_point(x_dict)
        classified_entities = []
        if len(categories) != len(x_dict["entities"]):
            errs.append(x)
            if handle_incorrect_llm:
                categories = [S_PURPOSE_CATEGORY_GENERAL] * len(x_dict["entities"])
            else:
                raise ValueError("The number of categories does not match the number of entities")
        for i, entity in enumerate(x_dict["entities"]):
            classified_entities.append(ClassifiedPurposeEntity(**{
                "category": map_purpose_to_level(categories[i], level=PURPOSE_MAPPING_LEVEL),
                **entity
            }))
        classified_purpose_entities.append(SWClassifiedPurposeEntities(**{"segment": x_dict["segment"], "entities": classified_entities}))

    return classified_purpose_entities, errs


def identify_parties(pp_text: str, segments: list[str], override_cache: PARAM_OVERRIDE_CACHE = None) -> list[SWPartyEntities]:
    """
    Identify the parties involved in the privacy policy

    @param pp_text: privacy policy text
    @return: list of parties, in the following form (as a list of SWPartyEntities):
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
    def call_llm_for_segment(segment_text):
        return qh.Q_PARTY_RECOGNITION.run_query({"segment": segment_text}, override_cache=override_cache)

    res = []
    for segment in tqdm(segments, leave=False, desc="Identifying parties"):
        entities = call_llm_for_segment(segment)
        res.append(SWPartyEntities(**{"segment": segment, "entities": entities}))
    return res


def identify_data_storage_locations(pp_text: str, segments: list[str], override_cache: PARAM_OVERRIDE_CACHE = None):
    # TODO: Not implemented yet!!!
    pass


def identify_data_storage_durations(pp_text: str, segments: list[str], override_cache: PARAM_OVERRIDE_CACHE = None):
    # TODO: Not implemented yet!!!
    pass


def identify_data_practices(pp_text: str, segments: list[str], override_cache: PARAM_OVERRIDE_CACHE = None) -> list[SWDataPractices]:
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
        parsed_model_output = qh.Q_ACTION_RECOGNITION.run_query({"segment": segment_text}, override_cache=override_cache)
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

    res = []
    for segment in tqdm(segments, leave=False, desc="Identifying data practices"):
        practices = call_llm_for_segment(segment)
        res.append(SWDataPractices(**{"segment": segment, "practices": practices}))
    return res


def identify_relations(relation_query, override_cache: PARAM_OVERRIDE_CACHE = None) -> list[Relation]:
    """
    Identify relations between data practice actions and entities in the privacy policy, through LLM

    @param relation_query: a query data for the LLM, which are elements from convert_grouped_practices_to_query_data
    @return: list of identified relations, in the following form (as a list of Relation):
    [
        {
            "action_id": ACTION_ID,
            "entity_id": ENTITY_ID,
            "relation": RELATION_TYPE
        }
    ]
    """

    return [Relation(**relation) for relation in qh.Q_RELATION_RECOGNITION.run_query(relation_query, override_cache=override_cache)]
