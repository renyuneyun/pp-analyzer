from dataclasses import dataclass
from functools import partial
from typing import Callable
import fine_tune.annotation_utils as a_utils
import fine_tune.llm_utils as llm_utils
import fine_tune.message_utils as m_utils
from fine_tune.env import (
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
    type: str | None = None


f_d4 = partial(std.better_split, num_split=[40, 80, 10, 20])


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
        desc="data_entity-sent_data-d3",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_span_of_sentence,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="data_entity-sent_data-v3-d3",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_span_of_sentence_only,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="data_entity-sent_data-v3-d4",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_span_of_sentence_only,
        training_data_splitter=f_d4,
    ),
    JobPreset(
        desc="data_entity-sent_data-v4-d3",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_span_of_sentence_only_weak_filter,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="data_entity-sent_data-v4-d4",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_span_of_sentence_only_weak_filter,
        training_data_splitter=f_d4,
    ),
    JobPreset(
        desc="data_entity_action-seg_data-d3",
        load_data=partial(a_utils.load_and_get, a_utils.get_data_entities_with_actions_of_segments),
        as_training_data=m_utils.as_training_data_for_data_span_with_action_of_segment,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="data_entity_action-sent_data-d3",
        load_data=partial(a_utils.load_and_get, a_utils.get_data_entities_with_actions_of_sentences),
        as_training_data=m_utils.as_training_data_for_data_span_with_action_of_sentence,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="data_entity_action-sent_data-d4",
        load_data=partial(a_utils.load_and_get, a_utils.get_data_entities_with_actions_of_sentences),
        as_training_data=m_utils.as_training_data_for_data_span_with_action_of_sentence,
        training_data_splitter=f_d4,
    ),
    JobPreset(
        desc="data_entity_action-sent_data-v2-d3",
        load_data=partial(a_utils.load_and_get, a_utils.get_data_entities_with_actions_of_sentences),
        as_training_data=m_utils.as_training_data_for_data_span_with_action_of_sentence_weak_filter,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="data_class-sent_data-v2",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_classification_of_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="data_class-sent_data-v2-d4",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_data_classification_of_segment,
        training_data_splitter=f_d4,
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
        desc="data_class-retrieval",
        load_data=a_utils.load_data_entities_of_segments,
        as_training_data=m_utils.as_query_data_directly,
        training_data_splitter=std.no_split,
        type="retrieval",
    ),
    JobPreset(
        desc="data_class-retrieval_sent",
        load_data=a_utils.load_data_entities_of_sentences,
        as_training_data=m_utils.as_query_data_directly,
        training_data_splitter=std.no_split,
        type="retrieval",
    ),
    JobPreset(
        desc="purpose_span-seg_entity-v2-d3",
        load_data=a_utils.load_purpose_entities_of_segments,
        as_training_data=m_utils.as_training_data_for_purpose_span_of_segment,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="purpose_span-sent_entity-v2",
        load_data=a_utils.load_purpose_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_purpose_span_of_sentence_only,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="purpose_span-sent_entity-d3",
        load_data=a_utils.load_purpose_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_purpose_span_of_sentence_only,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="purpose_span-sent_entity-v2-d3",
        load_data=a_utils.load_purpose_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_purpose_span_of_sentence_only_improved,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="purpose_span-sent_entity-v2-d4",
        load_data=a_utils.load_purpose_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_purpose_span_of_sentence_only_improved,
        training_data_splitter=f_d4,
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
        desc="purpose_class-sent_purpose-v2-d4",
        load_data=a_utils.load_purpose_entities_of_sentences,
        as_training_data=m_utils.as_training_data_for_purpose_classification_of_sentence,
        training_data_splitter=f_d4,
    ),
    JobPreset(
        desc="purpose_class-retrieval_sent",
        load_data=a_utils.load_purpose_entities_of_sentences,
        as_training_data=m_utils.as_query_data_directly,
        training_data_splitter=std.no_split,
        type="retrieval",
    ),
    JobPreset(
        desc="action-seg-v2",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_segments),
        as_training_data=m_utils.as_training_data_for_action_span_for_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="action-seg-v2-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_segments),
        as_training_data=m_utils.as_training_data_for_action_span_for_segment_v2,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="action-seg-v2-d3",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_segments),
        as_training_data=m_utils.as_training_data_for_action_span_for_segment_v2,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="action-sent-v2",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_sentences),
        as_training_data=m_utils.as_training_data_for_action_span_of_sentence_only,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="action-sent-v3-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_sentences),
        as_training_data=m_utils.as_training_data_for_action_span_of_sentence_only_improved,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="action-sent-v3-d3",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_sentences),
        as_training_data=m_utils.as_training_data_for_action_span_of_sentence_only_improved,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="action-sent-v3-d4",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_sentences),
        as_training_data=m_utils.as_training_data_for_action_span_of_sentence_only_improved,
        training_data_splitter=f_d4,
    ),
    JobPreset(
        desc="action-sent-v3-d5",
        load_data=partial(a_utils.load_and_get, a_utils.get_actions_of_sentences),
        as_training_data=m_utils.as_training_data_for_action_span_of_sentence_only_improved,
        training_data_splitter=partial(std.better_split, num_split=[102, 644, 21, 138]),  # Use 70% 15% for each type
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
    JobPreset(
        desc="pm-sent-v3",
        load_data=partial(a_utils.load_and_get, a_utils.get_protection_methods_of_sentences),
        as_training_data=m_utils.as_training_data_for_protection_method_of_sentence_only_with_details,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="party-seg-v2",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_segments),
        as_training_data=m_utils.as_training_data_for_party_entity_of_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="party-sent-v2",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_sentences),
        as_training_data=m_utils.as_training_data_for_party_entity_of_sentence,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="party-seg-v2-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_segments_v2),
        as_training_data=m_utils.as_training_data_for_party_entity_of_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="party-sent-v2-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_sentences_v2),
        as_training_data=m_utils.as_training_data_for_party_entity_of_sentence,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="party-seg-v3-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_segments_v2),
        as_training_data=m_utils.as_training_data_for_party_entity_of_segment_v2,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="party-sent-v3-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_sentences_v2),
        as_training_data=m_utils.as_training_data_for_party_entity_of_sentence_v2,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="party-seg-v3-d3",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_segments_v2),
        as_training_data=m_utils.as_training_data_for_party_entity_of_segment_v2,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="party-sent-v3-d3",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_sentences_v2),
        as_training_data=m_utils.as_training_data_for_party_entity_of_sentence_v2,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="party-sent-v3-d4",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_sentences_v2),
        as_training_data=m_utils.as_training_data_for_party_entity_of_sentence_v2,
        training_data_splitter=f_d4,
    ),
    JobPreset(
        desc="party-sent-v4-d3",
        load_data=partial(a_utils.load_and_get, a_utils.get_party_entities_of_sentences_v2),
        as_training_data=m_utils.as_training_data_for_party_entity_of_sentence_v3,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="relation-seg-v2",
        load_data=partial(a_utils.load_and_get, a_utils.get_relations_of_segment_sentences_no_subsume),
        as_training_data=m_utils.as_training_data_for_relation_of_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="relation-seg-v2-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_relations_of_segment_sentences_no_subsume_v2),
        as_training_data=m_utils.as_training_data_for_relation_of_segment,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="relation-seg-v3-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_relations_of_segment_sentences_no_subsume_v3),
        as_training_data=m_utils.as_training_data_for_relation_of_segment_renamed,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="relation-seg-v4-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_relations_of_segment_sentences_no_subsume_v3),
        as_training_data=m_utils.as_training_data_for_relation_of_segment_renamed_more_instruct,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="relation-sent-v4-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_relations_of_segment_sentences_no_subsume_v3),
        as_training_data=m_utils.as_training_data_for_relation_of_sentence,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="relation-sent-v4-d3",
        load_data=partial(a_utils.load_and_get, a_utils.get_relations_of_segment_sentences_no_subsume_v3),
        as_training_data=m_utils.as_training_data_for_relation_of_sentence,
        training_data_splitter=std.better_split_equal,
    ),
    JobPreset(
        desc="relation-sent-v5-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_relations_of_sentences_no_subsume),
        as_training_data=m_utils.as_training_data_for_relation_of_sentence_v2,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="subsume-sent-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_subsume_relations_of_sentences),
        as_training_data=m_utils.as_training_data_for_subsume_relation_of_sentence,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="subsume-sent-v2-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_subsume_relations_of_sentences),
        as_training_data=m_utils.as_training_data_for_subsume_relation_of_sentence_v2,
        training_data_splitter=std.better_split,
    ),
    JobPreset(
        desc="store_det-sent-d2",
        load_data=partial(a_utils.load_and_get, a_utils.get_retention_details_of_sentences),
        as_training_data=m_utils.as_training_data_for_retention_details_of_sentence,
        training_data_splitter=std.better_split,
    ),
]


JOB_PRESET = {
    preset.desc: preset
    for preset in _job_presets
}
