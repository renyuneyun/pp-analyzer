from copy import deepcopy
import csv
import json
import os
from .message_templates import *
from .env import (
    _data_category_definitions,
    _data_category_definitions_text,
    _data_category_hierarchy,
    _data_category_hierarchy_text,
    _purpose_category_definitions,
    _purpose_category_definitions_text,
    _purpose_category_hierarchy,
    _purpose_category_hierarchy_text,
)


def _as_training_data_entity_general(entities, system_message, user_message_fn, assistant_message_fn):
    data_template = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in entities:
        data = deepcopy(data_template)
        data["messages"][1]["content"] = user_message_fn(segment)
        data["messages"][2]["content"] = assistant_message_fn(segment)
        data_list.append(data)
    return data_list


def _as_training_data_entity_text(entities, system_message, user_message_fn):
    return _as_training_data_entity_general(entities, system_message, user_message_fn,
                                            lambda segment: json.dumps([a["text"] for a in segment["entities"]]))


def _as_training_data_entity_segment_text(entities, system_message, user_message_templace):
    return _as_training_data_entity_text(entities, system_message, lambda segment: user_message_templace.format(**segment))


def as_training_data_for_data_span_of_segment(data_entities_of_segments):
    return _as_training_data_entity_segment_text(data_entities_of_segments,
                                         SYSTEM_MESSAGE,
                                         USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION)


def as_training_data_for_data_span_of_segment_1_1(data_entities_of_segments):
    return _as_training_data_entity_segment_text(data_entities_of_segments,
                                            SYSTEM_MESSAGE,
                                            USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_1_1)


def as_training_data_for_data_span_of_sentence_only(data_entities_of_sentences):
    return _as_training_data_entity_segment_text(data_entities_of_sentences,
                                            SYSTEM_MESSAGE_DATA_ENTITY_RECOGNITION_SENTENCE,
                                            USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_SENTENCE)


def as_training_data_for_data_span_of_sentence_only_weak_filter(data_entities_of_sentences):
    return _as_training_data_entity_segment_text(data_entities_of_sentences,
                                            SYSTEM_MESSAGE_DATA_ENTITY_RECOGNITION_SENTENCE_WEAK_FILTER,
                                            USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_SENTENCE)


def as_training_data_for_data_span_of_sentence(data_entities_of_sentences):
    return _as_training_data_entity_segment_text(data_entities_of_sentences,
                                            SYSTEM_MESSAGE,
                                            USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2)


def as_training_data_for_data_span_of_sentence_1(data_entities_of_sentences):
    return _as_training_data_entity_segment_text(data_entities_of_sentences,
                                            SYSTEM_MESSAGE,
                                            USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2_1)


def as_training_data_for_data_span_with_action_of_segment(data_entities_of_segments):
    return _as_training_data_entity_general(data_entities_of_segments,
                                            SYSTEM_MESSAGE_DATA_ENTITY_RECOGNITION_WITH_ACTION,
                                            lambda segment: USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_WITH_ACTION.format(**segment),
                                            lambda segment: json.dumps([{
                                                "action_context": a["action_context"],
                                                "text": a["text"],
                                            } for a in segment["entities"]]))


def as_training_data_for_data_span_with_action_of_sentence(data_entities_of_sentence):
    return _as_training_data_entity_general(data_entities_of_sentence,
                                            SYSTEM_MESSAGE_DATA_ENTITY_RECOGNITION_WITH_ACTION,
                                            lambda segment: USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_WITH_ACTION.format(
                                                **{'segment': segment['sentence']}),
                                            lambda segment: json.dumps([{
                                                "action_context": a["action_context"],
                                                "text": a["text"],
                                            } for a in segment["entities"]]))


def as_training_data_for_data_span_with_action_of_sentence_weak_filter(data_entities_of_sentence):
    return _as_training_data_entity_general(data_entities_of_sentence,
                                            SYSTEM_MESSAGE_DATA_ENTITY_RECOGNITION_WITH_ACTION_WEAK_FILTER,
                                            lambda segment: USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_WITH_ACTION.format(
                                                **{'segment': segment['sentence']}),
                                            lambda segment: json.dumps([{
                                                "action_context": a["action_context"],
                                                "text": a["text"],
                                            } for a in segment["entities"]]))


def as_training_data_for_data_classification_of_segment(data_entities_of_segments):
    return _as_training_data_entity_general(data_entities_of_segments,
                                         SYSTEM_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION.format(
                                                hierarchy=_data_category_hierarchy_text,
                                                definitions=_data_category_definitions_text,
                                            ),
                                         lambda segment: USER_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION.format(**segment, phrases=json.dumps([e["text"] for e in segment["entities"]])),
                                         lambda segment: json.dumps([e["type"] for e in segment["entities"]]))


def as_training_data_for_data_classification_of_segment_gradual(data_entities_of_segments, level=0):
    if isinstance(level, int):
        level = [level]

    prompt_template = USER_MESSAGE_TEMPLATE_DATA_CATEGORY_CLASSIFICATION_GRADUAL

    data_list = []

    for l in level:
        category_string = '\n'.join([
            f"{category}, {_data_category_definitions[category]}"
            for category in _data_category_hierarchy.keys()
            ])  #Level = 0
        data_template = {
            "messages": [
                {"role": "system", "content":
                    SYSTEM_MESSAGE_TEMPLATE_DATA_CATEGORY_CLASSIFICATION_GRADUAL.format(
                        categories=category_string
                    )},
                {"role": "user", "content": None},
                {"role": "assistant", "content": None},
            ]}

        for segment in data_entities_of_segments:
            entities = segment["entities"]
            phrases = [e["text"] for e in entities]
            answers = [e["type"] for e in entities]
            prompt = prompt_template.format(
                segment=segment["segment"], phrases=json.dumps(phrases))
            data = deepcopy(data_template)
            data["messages"][1]["content"] = prompt
            data["messages"][2]["content"] = json.dumps(answers)
            data_list.append(data)
    return data_list


def as_training_data_for_purpose_span_of_segment(purpose_entities_of_segments):
    return _as_training_data_entity_segment_text(purpose_entities_of_segments,
                                            SYSTEM_MESSAGE_PURPOSE_ENTITY_RECOGNITION_SENTENCE_IMPROVED,
                                            USER_MESSAGE_TEMPLATE_PURPOSE_ENTITY_RECOGNITION)


def as_training_data_for_purpose_span_of_sentence_only(purpose_entities_of_sentences):
    return _as_training_data_entity_segment_text(purpose_entities_of_sentences,
                                            SYSTEM_MESSAGE_PURPOSE_ENTITY_RECOGNITION_SENTENCE,
                                            USER_MESSAGE_TEMPLATE_PURPOSE_ENTITY_RECOGNITION_SENTENCE)


def as_training_data_for_purpose_span_of_sentence_only_improved(purpose_entities_of_sentences):
    return _as_training_data_entity_segment_text(purpose_entities_of_sentences,
                                            SYSTEM_MESSAGE_PURPOSE_ENTITY_RECOGNITION_SENTENCE_IMPROVED,
                                            USER_MESSAGE_TEMPLATE_PURPOSE_ENTITY_RECOGNITION_SENTENCE)


def as_training_data_for_purpose_classification_of_segment(purpose_entities_of_segments):
    return _as_training_data_entity_general(purpose_entities_of_segments,
                                         SYSTEM_MESSAGE_TEMPLATE_PURPOSE_CATEGORY_CLASSIFICATION.format(
                                                hierarchy=_purpose_category_hierarchy_text,
                                                definitions=_purpose_category_definitions_text,
                                            ),
                                         lambda segment: USER_MESSAGE_TEMPLATE_PURPOSE_CATEGORY_CLASSIFICATION.format(**segment, phrases=json.dumps([e["text"] for e in segment["entities"]])),
                                         lambda segment: json.dumps([e["type"] for e in segment["entities"]]))


def as_training_data_for_purpose_classification_of_sentence(purpose_entities_of_sentence):
    return _as_training_data_entity_general(purpose_entities_of_sentence,
                                         SYSTEM_MESSAGE_TEMPLATE_PURPOSE_CATEGORY_CLASSIFICATION.format(
                                                hierarchy=_purpose_category_hierarchy_text,
                                                definitions=_purpose_category_definitions_text,
                                            ),
                                         lambda segment: USER_MESSAGE_TEMPLATE_PURPOSE_CATEGORY_CLASSIFICATION_SENTENCE.format(**segment, phrases=json.dumps([e["text"] for e in segment["entities"]])),
                                         lambda segment: json.dumps([e["type"] for e in segment["entities"]]))


def as_training_data_for_action_span_for_segment(action_entities_of_segments):
    data_template = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE_ACTION_RECOGNITION},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in action_entities_of_segments:
        data = deepcopy(data_template)
        data["messages"][1]["content"] = USER_MESSAGE_TEMPLATE_ACTION_RECOGNITION.format(**segment)
        for entity in segment["entities"]:
            data2 = deepcopy(data)
            data2["messages"][2]["content"] = json.dumps(entity)
            data_list.append(data2)
    return data_list


def as_training_data_for_action_span_for_segment_v2(action_entities_of_segments):
    return _as_training_data_entity_general(action_entities_of_segments,
                                            SYSTEM_MESSAGE_ACTION_RECOGNITION,
                                         lambda segment: USER_MESSAGE_TEMPLATE_ACTION_RECOGNITION.format(**segment),
                                         lambda segment: json.dumps(segment["entities"]))


def as_training_data_for_action_span_of_sentence_only(action_entities_of_segments):
    return _as_training_data_entity_general(action_entities_of_segments,
                                            SYSTEM_MESSAGE_ACTION_RECOGNITION_SENTENCE,
                                         lambda segment: USER_MESSAGE_TEMPLATE_ACTION_RECOGNITION_SENTENCE.format(**segment),
                                         lambda segment: json.dumps([a for a in segment["entities"]]))


def as_training_data_for_action_span_of_sentence_only_improved(action_entities_of_segments):
    return _as_training_data_entity_general(action_entities_of_segments,
                                            SYSTEM_MESSAGE_ACTION_RECOGNITION_SENTENCE_IMPROVED,
                                         lambda segment: USER_MESSAGE_TEMPLATE_ACTION_RECOGNITION_SENTENCE.format(**segment),
                                         lambda segment: json.dumps([a for a in segment["entities"]]))


def as_training_data_for_protection_method_of_segment(protection_method_entities_of_segments):
    return _as_training_data_entity_general(protection_method_entities_of_segments,
                                         SYSTEM_MESSAGE_PROTECTION_METHOD,
                                         lambda segment: USER_MESSAGE_TEMPLATE_PROTECTION_METHOD.format(**segment),
                                         lambda segment: json.dumps([{"protection-method": e["type"], "text": e["text"]} for e in segment["entities"]]))


def as_training_data_for_protection_method_of_sentence_only(protection_method_entities_of_sentences):
    return _as_training_data_entity_general(protection_method_entities_of_sentences,
                                         SYSTEM_MESSAGE_PROTECTION_METHOD,
                                         lambda segment: USER_MESSAGE_TEMPLATE_PROTECTION_METHOD_SENTENCE.format(**segment),
                                         lambda segment: json.dumps([{"protection-method": e["type"], "text": e["text"]} for e in segment["entities"]]))


def as_training_data_for_protection_method_of_sentence_only_with_details(protection_method_entities_of_sentences):
    return _as_training_data_entity_general(protection_method_entities_of_sentences,
                                         SYSTEM_MESSAGE_PROTECTION_METHOD_DETAILS,
                                         lambda segment: USER_MESSAGE_TEMPLATE_PROTECTION_METHOD_SENTENCE.format(**segment),
                                         lambda segment: json.dumps([{"protection-method": e["type"], "text": e["text"]} for e in segment["entities"]]))


def as_training_data_for_party_entity_of_segment(protection_method_entities_of_segments):
    return _as_training_data_entity_general(protection_method_entities_of_segments,
                                            SYSTEM_MESSAGE_PARTY_RECOGNITION,
                                         lambda segment: USER_MESSAGE_TEMPLATE_PARTY_RECOGNITION.format(**segment),
                                         lambda segment: json.dumps([{"party_type": e["type"], "text": e["text"]} for e in segment["entities"]]))


def as_training_data_for_party_entity_of_sentence(protection_method_entities_of_sentences):
    return _as_training_data_entity_general(protection_method_entities_of_sentences,
                                            SYSTEM_MESSAGE_PARTY_RECOGNITION,
                                         lambda segment: USER_MESSAGE_TEMPLATE_PARTY_RECOGNITION_SENTENCE.format(**segment),
                                         lambda segment: json.dumps([{"party_type": e["type"], "text": e["text"]} for e in segment["entities"]]))


def as_training_data_for_party_entity_of_segment_v2(protection_method_entities_of_segments):
    return _as_training_data_entity_general(protection_method_entities_of_segments,
                                            SYSTEM_MESSAGE_PARTY_RECOGNITION_V2,
                                         lambda segment: USER_MESSAGE_TEMPLATE_PARTY_RECOGNITION.format(**segment),
                                         lambda segment: json.dumps([{"party_type": e["type"], "text": e["text"]} for e in segment["entities"]]))


def as_training_data_for_party_entity_of_sentence_v2(protection_method_entities_of_sentences):
    return _as_training_data_entity_general(protection_method_entities_of_sentences,
                                            SYSTEM_MESSAGE_PARTY_RECOGNITION_V2,
                                         lambda segment: USER_MESSAGE_TEMPLATE_PARTY_RECOGNITION_SENTENCE.format(**segment),
                                         lambda segment: json.dumps([{"party_type": e["type"], "text": e["text"]} for e in segment["entities"]]))


def as_training_data_for_party_entity_of_sentence_v3(protection_method_entities_of_sentences):
    return _as_training_data_entity_general(protection_method_entities_of_sentences,
                                            SYSTEM_MESSAGE_PARTY_RECOGNITION_V3,
                                         lambda segment: USER_MESSAGE_TEMPLATE_PARTY_RECOGNITION_SENTENCE.format(**segment),
                                         lambda segment: json.dumps([{"party_type": e["type"], "text": e["text"]} for e in segment["entities"]]))


def _as_training_data_for_relation_of_segment(relation_entities_of_segments, system_message, user_message_templace):
    data_template = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in relation_entities_of_segments:
        segment_text = segment['segment']
        action_type_list = []
        entity_list = []
        relations = []
        for e in segment['entities']:
            sentence = e['sentence']
            action_type = e['action_type']
            action_id = f"C{len(action_type_list)}"
            action_type_list.append({
                "id": action_id,
                "action_type": action_type,
                "text": sentence,
            })
            for r in e['relations']:
                relation_type = r['relation_type']
                entity_text = r['entity']
                entity_type = r['entity_type']
                entity_id = f"D{len(entity_list)}"
                entity_list.append({
                    "id": entity_id,
                    "type": entity_type,
                    "text": entity_text,
                })
                relations.append({
                    "action_id": action_id,
                    "entity_id": entity_id,
                    "relation": relation_type,
                })
        user_message = user_message_templace.format(**{
            'segment': segment_text,
            'targets': {
                "action_contexts": action_type_list,
                "entities": entity_list,
            }
        })
        reply = json.dumps(relations)

        data = deepcopy(data_template)
        data["messages"][1]["content"] = user_message
        data["messages"][2]["content"] = reply
        data_list.append(data)
    return data_list


def as_training_data_for_relation_of_segment(relation_entities_of_segments):
    return _as_training_data_for_relation_of_segment(relation_entities_of_segments,
                                                     SYSTEM_MESSAGE_RELATION_RECOGNITION,
                                                     USER_MESSAGE_TEMPLATE_RELATION_RECOGNITION)


def as_training_data_for_relation_of_segment_renamed(relation_entities_of_segments):
    return _as_training_data_for_relation_of_segment(relation_entities_of_segments,
                                                     SYSTEM_MESSAGE_RELATION_RECOGNITION_RENAMED,
                                                     USER_MESSAGE_TEMPLATE_RELATION_RECOGNITION)


def as_training_data_for_relation_of_segment_renamed_more_instruct(relation_entities_of_segments):
    return _as_training_data_for_relation_of_segment(relation_entities_of_segments,
                                                     SYSTEM_MESSAGE_RELATION_RECOGNITION_RENAMED_MORE_INSTRUCT,
                                                     USER_MESSAGE_TEMPLATE_RELATION_RECOGNITION)


def as_training_data_for_relation_of_sentence(relation_entities_of_segments):
    data_template = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE_RELATION_RECOGNITION_RENAMED_MORE_INSTRUCT},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in relation_entities_of_segments:
        for e in segment['entities']:
            sentence = e['sentence']
            action_type_list = []
            entity_list = []
            relations = []
            action_type = e['action_type']
            action_id = f"C{len(action_type_list)}"
            action_type_list.append({
                "id": action_id,
                "action_type": action_type,
                "text": sentence,
            })
            for r in e['relations']:
                relation_type = r['relation_type']
                entity_text = r['entity']
                entity_type = r['entity_type']
                entity_id = f"D{len(entity_list)}"
                entity_list.append({
                    "id": entity_id,
                    "type": entity_type,
                    "text": entity_text,
                })
                relations.append({
                    "action_id": action_id,
                    "entity_id": entity_id,
                    "relation": relation_type,
                })

            user_message = USER_MESSAGE_TEMPLATE_RELATION_RECOGNITION_SENTENCE.format(**{
                'sentence': sentence,
                'targets': {
                    "action_contexts": action_type_list,
                    "entities": entity_list,
                }
            })
            reply = json.dumps(relations)

            data = deepcopy(data_template)
            data["messages"][1]["content"] = user_message
            data["messages"][2]["content"] = reply
            data_list.append(data)
    return data_list


def as_training_data_for_relation_of_sentence_v2(relation_entities_of_segments):
    '''
    Uses the real sentence data from `get_relations_of_sentences_no_subsume()`
    '''
    data_template = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE_RELATION_RECOGNITION_RENAMED_MORE_INSTRUCT},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in relation_entities_of_segments:
        sentence = segment['sentence']
        action_type_list = []
        entity_list = []
        relations = []
        for e in segment['entities']:
            action_type = e['action_type']
            action_id = f"C{len(action_type_list)}"
            action_type_list.append({
                "id": action_id,
                "action_type": action_type,
                "text": sentence,
            })
            for r in e['relations']:
                relation_type = r['relation_type']
                entity_text = r['entity']
                entity_type = r['entity_type']
                entity_id = f"D{len(entity_list)}"
                entity_list.append({
                    "id": entity_id,
                    "type": entity_type,
                    "text": entity_text,
                })
                relations.append({
                    "action_id": action_id,
                    "entity_id": entity_id,
                    "relation": relation_type,
                })

        user_message = USER_MESSAGE_TEMPLATE_RELATION_RECOGNITION_SENTENCE.format(**{
            'sentence': sentence,
            'targets': {
                "action_contexts": action_type_list,
                "entities": entity_list,
            }
        })
        reply = json.dumps(relations)

        data = deepcopy(data_template)
        data["messages"][1]["content"] = user_message
        data["messages"][2]["content"] = reply
        data_list.append(data)
    return data_list


def as_training_data_for_subsume_relation_of_segment_sentence(subsume_relation_entities_of_segments):
    data_template = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE_SUBSUME_RELATION_RECOGNITION_SENTENCE},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in subsume_relation_entities_of_segments:
        for e in segment['entities']:
            sentence = e['sentence']
            entity_ids = {}  # span -> id
            entities = []  # [{"id": id, "text": text}]
            relations = [] # [{"subsuming": id, "subsumed": id}]
            for r in e['relations']:
                subsumed_entity_text, subsumed_entity_span = r['subsumed']
                subsuming_entity_text, subsuming_entity_span = r['subsuming']

                if subsumed_entity_span not in entity_ids:
                    entity_ids[subsumed_entity_span] = f"D{len(entity_ids)}"
                    entities.append({"id": entity_ids[subsumed_entity_span], "text": subsumed_entity_text})
                subsumed_entity_id = entity_ids[subsumed_entity_span]

                if subsuming_entity_span not in entity_ids:
                    entity_ids[subsuming_entity_span] = f"D{len(entity_ids)}"
                    entities.append({"id": entity_ids[subsuming_entity_span], "text": subsuming_entity_text})
                subsuming_entity_id = entity_ids[subsuming_entity_span]

                relations.append({
                    "subsuming": subsuming_entity_id,
                    "subsumed": subsumed_entity_id,
                })

            user_message = USER_MESSAGE_TEMPLATE_SUBSUME_RELATION_RECOGNITION_SENTENCE.format(**{
                'sentence': sentence,
                'targets': {
                    "entities": entities,
                }
            })
            reply = json.dumps(relations)

            data = deepcopy(data_template)
            data["messages"][1]["content"] = user_message
            data["messages"][2]["content"] = reply
            data_list.append(data)
    return data_list


def _as_training_data_for_subsume_relation_of_sentence(subsume_relation_entities_of_sentences, system_message):
    data_template = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for sentence_obj in subsume_relation_entities_of_sentences:
        sentence = sentence_obj['sentence']
        entity_ids = {}  # span -> id
        entities = []  # [{"id": id, "text": text}]
        relations = [] # [{"subsuming": id, "subsumed": id}]
        for r in sentence_obj['entities']:
            subsumed_entity_text, subsumed_entity_span = r['subsumed']
            subsuming_entity_text, subsuming_entity_span = r['subsuming']

            if subsumed_entity_span not in entity_ids:
                entity_ids[subsumed_entity_span] = f"D{len(entity_ids)}"
                entities.append({"id": entity_ids[subsumed_entity_span], "text": subsumed_entity_text})
            subsumed_entity_id = entity_ids[subsumed_entity_span]

            if subsuming_entity_span not in entity_ids:
                entity_ids[subsuming_entity_span] = f"D{len(entity_ids)}"
                entities.append({"id": entity_ids[subsuming_entity_span], "text": subsuming_entity_text})
            subsuming_entity_id = entity_ids[subsuming_entity_span]

            relations.append({
                "subsuming": subsuming_entity_id,
                "subsumed": subsumed_entity_id,
            })

        user_message = USER_MESSAGE_TEMPLATE_SUBSUME_RELATION_RECOGNITION_SENTENCE.format(**{
            'sentence': sentence,
            'targets': {
                "entities": entities,
            }
        })
        reply = json.dumps(relations)

        data = deepcopy(data_template)
        data["messages"][1]["content"] = user_message
        data["messages"][2]["content"] = reply
        data_list.append(data)
    return data_list


def as_training_data_for_subsume_relation_of_sentence(subsume_relation_entities_of_sentences):
    return _as_training_data_for_subsume_relation_of_sentence(subsume_relation_entities_of_sentences, SYSTEM_MESSAGE_SUBSUME_RELATION_RECOGNITION_SENTENCE)


def as_training_data_for_subsume_relation_of_sentence_v2(subsume_relation_entities_of_sentences):
    return _as_training_data_for_subsume_relation_of_sentence(subsume_relation_entities_of_sentences, SYSTEM_MESSAGE_SUBSUME_RELATION_RECOGNITION_SENTENCE_V2)


def as_training_data_for_retention_details_of_sentence(retention_details_of_sentence):
    def get_assistant_message(segment):
        ret = []
        for item in segment['items']:
            dic = {}
            if 'storage-place' in item:
                dic['storage-place'] = item['storage-place']
            if 'retention-period' in item:
                dic['retention-period'] = item['retention-period']
            ret.append(dic)
        return json.dumps(ret)
    return _as_training_data_entity_general(retention_details_of_sentence, SYSTEM_MESSAGE_RETENTION_DETAILS,
                                            lambda segment: USER_MESSAGE_TEMPLATE_RETENTION_DETAILS.format(**{
                                                'segment': segment['sentence'],
                                                'targets': json.dumps([a['text'] for a in segment['items']]),
                                            }),
                                            get_assistant_message)


def as_query_data_directly(data_entities_of_segments):
    '''
    Return the list of entity texts directly, without prompt templates.
    '''
    data_list = []
    for segment in data_entities_of_segments:
        phrases = [e["text"] for e in segment["entities"]]
        results = [e["type"] for e in segment["entities"]]
        data_list.append((phrases, results))
    return data_list
