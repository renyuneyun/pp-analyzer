from copy import deepcopy
import csv
from dotenv import load_dotenv
import json
import os
from .message_templates import *
from .annotation_utils import (
    get_data_category_definitions,
    get_data_category_hierarchy,
)


load_dotenv()

F_DATA_CATEGORY_HIERARCHY = os.environ.get("DATA_CATEGORY_HIERARCHY")
F_DATA_CATEGORY_DEFINITION = os.environ.get("DATA_CATEGORY_DEFINITION") or os.environ.get("DATA_DEF_FILE")

if F_DATA_CATEGORY_DEFINITION:
    with open(F_DATA_CATEGORY_DEFINITION, "r") as f:
        _data_category_definitions_text = f.read()
    _data_category_definitions = get_data_category_definitions(F_DATA_CATEGORY_DEFINITION)

if F_DATA_CATEGORY_HIERARCHY:
    with open(F_DATA_CATEGORY_HIERARCHY, "r") as f:
        _data_category_hierarchy_text = f.read()
    _data_category_hierarchy = get_data_category_hierarchy(F_DATA_CATEGORY_HIERARCHY)


def as_training_data_for_data_span_of_segment(data_entities_of_segments):
    prompt_template = USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION
    data_template = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in data_entities_of_segments:
        prompt = prompt_template.format(segment=segment["segment"])
        answers = segment["entities"]
        # Keep only the text in answers
        answers = [a["text"] for a in answers]
        data = deepcopy(data_template)
        data["messages"][1]["content"] = prompt
        data["messages"][2]["content"] = json.dumps(answers)
        data_list.append(data)
    return data_list


def as_training_data_for_data_span_of_segment_1_1(data_entities_of_segments):
    prompt_template = USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_1_1
    data_template = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in data_entities_of_segments:
        prompt = prompt_template.format(segment=segment["segment"])
        answers = segment["entities"]
        # Keep only the text in answers
        answers = [a["text"] for a in answers]
        data = deepcopy(data_template)
        data["messages"][1]["content"] = prompt
        data["messages"][2]["content"] = json.dumps(answers)
        data_list.append(data)
    return data_list


def as_training_data_for_data_span_of_sentence_only(data_entities_of_sentences):
    prompt_template = USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_SENTENCE
    data_template = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE_DATA_ENTITY_RECOGNITION_SENTENCE},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in data_entities_of_sentences:
        prompt = prompt_template.format(**segment)
        answers = segment["entities"]
        # Keep only the text in answers
        answers = [a["text"] for a in answers]
        data = deepcopy(data_template)
        data["messages"][1]["content"] = prompt
        data["messages"][2]["content"] = json.dumps(answers)
        data_list.append(data)
    return data_list


def as_training_data_for_data_span_of_sentence(data_entities_of_sentences):
    prompt_template = USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2
    data_template = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in data_entities_of_sentences:
        prompt = prompt_template.format(**segment)
        answers = segment["entities"]
        # Keep only the text in answers
        answers = [a["text"] for a in answers]
        data = deepcopy(data_template)
        data["messages"][1]["content"] = prompt
        data["messages"][2]["content"] = json.dumps(answers)
        data_list.append(data)
    return data_list


def as_training_data_for_data_span_of_sentence_1(data_entities_of_sentences):
    prompt_template = USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2_1
    data_template = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in data_entities_of_sentences:
        prompt = prompt_template.format(**segment)
        answers = segment["entities"]
        # Keep only the text in answers
        answers = [a["text"] for a in answers]
        data = deepcopy(data_template)
        data["messages"][1]["content"] = prompt
        data["messages"][2]["content"] = json.dumps(answers)
        data_list.append(data)
    return data_list


def as_training_data_for_data_classification_of_segment(data_entities_of_segments):
    # Prompt is adpted and very briefly modified based on Vlad's original prompt. It may not be the best one as usage is different.
    prompt_template = USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION
    data_template = {
        "messages": [
            {"role": "system", "content":
                SYSTEM_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION.format(
                    hierarchy=_data_category_hierarchy_text,
                    definitions=_data_category_definitions_text,
                )},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}

    data_list = []

    for segment in data_entities_of_segments:
        entities = segment["entities"]
        phrases = [e["text"] for e in entities]
        answers = [e["type"] for e in entities]
        prompt = prompt_template.format(segment=segment["segment"], phrases=json.dumps(phrases))
        data = deepcopy(data_template)
        data["messages"][1]["content"] = prompt
        data["messages"][2]["content"] = json.dumps(answers)
        data_list.append(data)
    return data_list

def as_training_data_for_data_classification_of_segment_gradual(data_entities_of_segments, level=0):
    if isinstance(level, int):
        level = [level]

    prompt_template = USER_MESSAGE_TEMPLATE_DATA_CATEGORY_CLASSIFICATION_GRADUAL

    data_list = []

    for l in level:
        category_string = '\n'.join([
            f"{category}, {_data_category_definitions[category]}"
            for category in _data_category_hierarchy.keys()
            ]),  #Level = 0
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