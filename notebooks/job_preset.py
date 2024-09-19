from dataclasses import dataclass
from functools import partial
from typing import Callable
import src.annotation_utils as a_utils
import src.llm_utils as llm_utils
import src.message_utils as m_utils
from src.env import (
    BRAT_DATA_PATH,
)
import split_training_data as std


type DATA_ENTITIES = list
type DATA_AS_MESSAGES = list


@dataclass
class JobPreset:
    desc: str
    load_data: Callable[[], DATA_ENTITIES]
    as_training_data: Callable[[DATA_ENTITIES], DATA_AS_MESSAGES]
    training_data_splitter: Callable[[DATA_ENTITIES], tuple[list[int], list[int]]]


_job_presets = [
    JobPreset(
        desc="data_entity-sent_data-ver2",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_span_of_sentence,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="data_entity-seg_sent_data-v2",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_span_of_sentence,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="data_class-sent_data-v2",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_classification_of_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="data_class-sent_data_l0-v2",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_classification_of_segment_gradual,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="data_class-seg_data-v2",
        load_data=a_utils.load_data_entities_of_segments,
        as_training_data=m_utils.as_training_data_for_data_classification_of_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="data_class-seg_data_l0-v2",
        load_data=a_utils.load_data_entities_of_segments,
        as_training_data=m_utils.as_training_data_for_data_classification_of_segment_gradual,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="purpose_span-sent_entity-v2",
        load_data=a_utils.load_purpose_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_purpose_span_of_sentence_only,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="purpose_class-seg_purpose-v2",
        load_data=a_utils.load_purpose_entities_of_segments,
        as_training_data=m_utils.as_training_data_for_purpose_classification_of_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="purpose_class-sent_purpose-v2",
        load_data=a_utils.load_purpose_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_purpose_classification_of_sentence,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="action-seg-v2",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_segments),
        as_training_data=m_utils.as_training_data_for_action_span_for_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="action-sent-v2",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_sentences),
        as_training_data=m_utils.as_training_data_for_action_span_of_sentence_only,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="pm-seg-v2",
        load_data=partial(a_utils.load_and_get, a_utils.get_protection_methods_of_segments),
        as_training_data=m_utils.as_training_data_for_protection_method_of_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="pm-sent-v2",
        load_data=partial(a_utils.load_and_get, a_utils.get_protection_methods_of_sentences),
        as_training_data=m_utils.as_training_data_for_protection_method_of_sentence_only,
        training_data_splitter=std.better_split,
    ),
]


JOB_PRESET = {
    preset.desc: preset
    for preset in _job_presets
}
