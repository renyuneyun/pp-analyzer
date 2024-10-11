from .data_model import (
    to_dict,
    SWClassifiedDataEntities,
    SWClassifiedPurposeEntities,
    SWPartyEntities,
    SWDataPractices,
    SWGroupedDataPractice,
    SWGroupedDataPracticeWithId,
)


def group_data_practices_and_entities(
    data_practices: list[SWDataPractices], classified_data_entities: list[SWClassifiedDataEntities], classified_purpose_entities: list[SWClassifiedPurposeEntities], parties: list[SWPartyEntities]
) -> list[SWGroupedDataPractice]:
    """
    Group relevant information into the data practices.
    All entities are grouped by segments.

    @param data_practices: list of data practices, obtained from identify_data_practices
    @param classified_data_entities: list of data entities with categories, obtained from classify_data_categories
    @param classified_purpose_entities: list of purpose entities with categories, obtained from classify_purpose_categories
    @param parties: list of parties, obtained from identify_parties
    @return: list of data practices with relevant information, in the following form (as a list of SWGroupedDataPractice):
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
        for segment in to_dict(classified_purpose_entities)
    }
    indexed_parties = {
        segment["segment"]: segment["entities"] if "entities" in segment else []
        for segment in to_dict(parties)
    }

    res = []

    for isegment in data_practices:
        segment = to_dict(isegment)
        segment_text = segment["segment"]
        practices = segment["practices"]
        practice_parties = indexed_parties[segment_text] if segment_text in indexed_parties else []
        practice_data = indexed_data_entities[segment_text] if segment_text in indexed_data_entities else []
        practice_purpose = indexed_purpose_entities[segment_text] if segment_text in indexed_purpose_entities else []
        res.append(SWGroupedDataPractice(
            **{
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
            })
        )
    return res


def add_ids_into_grouped_practices(grouped_practices: list[SWGroupedDataPractice]) -> list[SWGroupedDataPracticeWithId]:
    """
    Add IDs into the grouped practices, for both practices and entities.
    The ID is simply the index of the data practice or entity in the list, and only serves the purpose of internal identification.
    Note that IDs are grouped by segments, so the same ID may appear in different segments.

    @param grouped_practices: list of grouped data practices, obtained from group_data_practices_and_entities
    @return: list of grouped data practices with IDs, in the following form (as a list of SWGroupedDataPracticeWithId):
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
    res = []
    for segment in grouped_practices:
        segment_text = segment.segment
        entity_counter = 0
        practices_with_id = []
        practices = to_dict(segment.practices)
        for practice_index, practice in enumerate(practices):
            practice_with_id = {
                "id": f"C{practice_index+1}",
                **practice
            }
            for party in practice_with_id["parties"]:
                entity_counter += 1
                party["id"] = f"D{entity_counter}"
            for data in practice_with_id["data"]:
                entity_counter += 1
                data["id"] = f"D{entity_counter}"
            for purpose in practice_with_id["purpose"]:
                entity_counter += 1
                purpose["id"] = f"D{entity_counter}"
            practices_with_id.append(practice_with_id)
        res.append(SWGroupedDataPracticeWithId(**{
            "segment": segment_text,
            "practices": practices_with_id
            }))
    return res


def convert_grouped_practices_to_query_data(grouped_practices_with_id: SWGroupedDataPracticeWithId):
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
    segment = to_dict(grouped_practices_with_id)
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
                "type": entity["party_type"],
            }
            entities.append(entity_info)
    res = {
        "segment": segment_text,
        "targets": {"action_contexts": action_contexts, "entities": entities},
    }
    return res