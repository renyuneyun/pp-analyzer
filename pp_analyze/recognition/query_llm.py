from copy import deepcopy
from . import query_helper as qh
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
        parsed_model_output = qh.Q_DATA_ENTITY.run_query({"segment": segment_text})
        res = []
        for entity in parsed_model_output:
            entity_text = entity
            start_pos = segment_text.find(entity_text)
            end_pos = start_pos + len(entity_text)
            span = (start_pos, end_pos)
            res.append({"text": entity_text, "span": span})
        return res

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
        return qh.Q_DATA_CLASSIFICATION.run_query({
            'segment': data_point['segment'],
            'phrases': [entity['text'] for entity in data_point['entities']]
        })

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


def identity_purpose_entities(pp_text: str, segments: list[str]) -> list[SWPurposeEntities]:
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
        parsed_model_output = qh.Q_PURPOSE_ENTITY.run_query({"segment": segment_text})
        res = []
        for entity in parsed_model_output:
            entity_text = entity
            start_pos = segment_text.find(entity_text)
            end_pos = start_pos + len(entity_text)
            span = (start_pos, end_pos)
            res.append({"text": entity_text, "span": span})
        return res

    res = []
    for segment in segments:
        entities = call_llm_for_segment(segment)
        res.append(SWPurposeEntities(**{"segment": segment, "entities": entities}))
    return res


def classify_purpose_categories(pp_text: str, segments: list[str], purpose_entities: list[SWPurposeEntities]) -> list[SWClassifiedPurposeEntities]:
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
        })

    purpose_entities = deepcopy(purpose_entities)
    classified_purpose_entities = []
    for x in purpose_entities:
        x_dict = to_dict(x)
        categories = call_llm_for_data_point(x_dict)
        classified_entities = []
        assert len(categories) == len(x_dict["entities"]), 'LLM did not return the correct number of categories'
        for i, entity in enumerate(x_dict["entities"]):
            classified_entities.append(ClassifiedPurposeEntity(**{
                "category": categories[i],
                **entity
            }))
        classified_purpose_entities.append(SWClassifiedPurposeEntities(**{"segment": x_dict["segment"], "entities": classified_entities}))

    return classified_purpose_entities


def identify_parties(pp_text: str, segments: list[str]) -> list[SWPartyEntities]:
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
        return qh.Q_PARTY_RECOGNITION.run_query({"segment": segment_text})

    res = []
    for segment in segments:
        entities = call_llm_for_segment(segment)
        res.append(SWPartyEntities(**{"segment": segment, "entities": entities}))
    return res


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
        parsed_model_output = qh.Q_ACTION_RECOGNITION.run_query({"segment": segment_text})
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
    for segment in segments:
        practices = call_llm_for_segment(segment)
        res.append(SWDataPractices(**{"segment": segment, "practices": practices}))
    return res


def identify_relations(relation_query) -> list[Relation]:
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

    return [Relation(**relation) for relation in qh.Q_RELATION_RECOGNITION.run_query(relation_query)]