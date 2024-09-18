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
    F_DATA_CATEGORY_HIERARCHY,
    F_DATA_CATEGORY_DEFINITION,
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
                                            SYSTEM_MESSAGE,
                                            USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_SENTENCE)


def as_training_data_for_data_span_of_sentence(data_entities_of_sentences):
    return _as_training_data_entity_segment_text(data_entities_of_sentences,
                                            SYSTEM_MESSAGE,
                                            USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2)


def as_training_data_for_data_span_of_sentence_1(data_entities_of_sentences):
    return _as_training_data_entity_segment_text(data_entities_of_sentences,
                                            SYSTEM_MESSAGE,
                                            USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2_1)


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


def as_training_data_for_purpose_span_of_sentence_only(purpose_entities_of_sentences):
    return _as_training_data_entity_segment_text(purpose_entities_of_sentences,
                                            SYSTEM_MESSAGE_PURPOSE_ENTITY_RECOGNITION_SENTENCE,
                                            USER_MESSAGE_TEMPLATE_PURPOSE_ENTITY_RECOGNITION_SENTENCE)


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
