import json
import numpy as np
from pprint import pprint
from pydantic import BaseModel, Field
import pylcs
from typing import Optional
from ppa_commons import (
    DataType,
    heuristic_extract_entities,
    try_parse_json_object,
)


def lcs_rate(a, b):
    if isinstance(a, str) and isinstance(b, str):
        rate = pylcs.lcs_sequence_length(a, b) / len(a) if a else 0  # Similar to precision
    else:
        rate = a.lcs_rate(b)
    if rate > 1:
        rate = 1
    return rate


class DataPoint(BaseModel):
    class Config:
        frozen = True


class EntityWithActionDataPoint(DataPoint):
    action_context: str
    text: str

    def lcs_rate(self, o):
        return min(
            pylcs.lcs_sequence_length(self.action_context, o.action_context) / len(self.action_context),
            pylcs.lcs_sequence_length(self.text, o.text) / len(self.text)
            )


class ActionDataPoint(DataPoint):
    action_type: str
    text: str
    sentence: Optional[str] = None

    def lcs_rate(self, o):
        if self.action_type != o.action_type:
            return 0
        if self.sentence is None:
            return pylcs.lcs_sequence_length(self.text, o.text) / len(self.text)
        else:
            return min(pylcs.lcs_sequence_length(self.text, o.text) / len(self.text), pylcs.lcs_sequence_length(self.sentence, o.sentence) / len(self.sentence))


class ProtectionMethodDataPoint(DataPoint):
    protection_method: str = Field(alias='protection-method')
    text: str

    def lcs_rate(self, o):
        rate1 = pylcs.lcs_sequence_length(self.protection_method, o.protection_method) / len(self.protection_method) if self.protection_method else 0
        rate2 = pylcs.lcs_sequence_length(self.text, o.text) / len(self.text) if self.text else 0
        return min(rate1, rate2)
        if self.protection_method != o.protection_method:
            return 0
        return pylcs.lcs_sequence_length(self.text, o.text) / len(self.text) if self.text else 0


class PartyDataPoint(DataPoint):
    party_type: str
    text: str

    def lcs_rate(self, o):
        if self.party_type != o.party_type:
            return 0
        return pylcs.lcs_sequence_length(self.text, o.text) / len(self.text) if self.text else 0


class RelationDataPoint(DataPoint):
    relation: str
    action_id: str
    entity_id: str

    def lcs_rate(self, o):
        return pylcs.lcs_sequence_length(self.relation, o.relation) / len(self.relation) if self.relation else 0


class RetentionDetailsDataPoint(DataPoint):
    storage_place: str | None = Field(alias='storage-place', default=None)
    retention_period: str | None = Field(alias='retention-period', default=None)

    def lcs_rate(self, o):
        rate1 = pylcs.lcs_sequence_length(self.storage_place, o.storage_place) / len(self.storage_place) if self.storage_place else 0
        if self.storage_place == o.storage_place:
            rate1 = 1
        rate2 = pylcs.lcs_sequence_length(self.retention_period, o.retention_period) / len(self.retention_period) if self.retention_period else 0
        if self.retention_period == o.retention_period:
            rate2 = 1
        return min(rate1, rate2)


_data_type_to_class = {
    DataType.ENTITY_WITH_ACTION: EntityWithActionDataPoint,
    DataType.ACTION: ActionDataPoint,
    DataType.PROTECTION_METHOD: ProtectionMethodDataPoint,
    DataType.PARTY: PartyDataPoint,
    DataType.RELATION: RelationDataPoint,
    DataType.RETENTION_DETAILS: RetentionDetailsDataPoint,
}


def precision_accuracy_f1(expected, predicted, data_type=DataType.ENTITY, lcs_threshold=None, tolerate_additionally_predicted=None, ignore_order=True, **kwargs):
    if data_type == DataType.PARTY and tolerate_additionally_predicted is None:
        tolerate_additionally_predicted = True
    if ignore_order:
        if data_type == DataType.ENTITY:
            expected = set(expected)
            predicted = set(predicted)
        elif data_type == DataType.ACTION:
            if isinstance(expected, dict):
                expected = [expected]
            try:
                expected = set([ActionDataPoint(**obj) for obj in expected])
                predicted = set([ActionDataPoint(**obj) for obj in predicted])
            except Exception as e:
                # print(f"Error in parsing action data point: {e};\n  expected: {expected};\n  predicted: {predicted}")
                raise e
        elif data_type in _data_type_to_class:
            cls = _data_type_to_class[data_type]
            expected = set([cls(**obj) for obj in expected])
            predicted = set([cls(**obj) for obj in predicted])
        else:
            raise ValueError(f"Unrecognised data_type: {data_type}")

        intersection = expected.intersection(predicted)
        intersection_with_lcs = len(intersection)
        only_in_expected = list(expected - predicted)
        only_in_predicted = list(predicted - expected)
        if lcs_threshold is not None:
            used = []  # Greedy. Probably underestimating, but efficient and mostly near-correct.
            for e1 in only_in_expected:
                maximum_lcs_rate = 0
                maximum_lcs_index = -1
                for i, e2 in enumerate(only_in_predicted):
                    if i in used: continue
                    ilcs_rate = lcs_rate(e1, e2)
                    if ilcs_rate > maximum_lcs_rate:
                        maximum_lcs_rate = ilcs_rate
                        maximum_lcs_index = i
                if maximum_lcs_rate >= lcs_threshold:
                    if lcs_threshold == -1 and data_type == DataType.ENTITY:
                        if maximum_lcs_rate > 0:
                            words1 = e1.split()
                            words2 = only_in_predicted[maximum_lcs_index].split()
                            if set(words1) & set(words2):
                                intersection_with_lcs += 1
                    else:
                        intersection_with_lcs += maximum_lcs_rate
                    used.append(maximum_lcs_index)

        if not expected and not predicted:
            precision = recall = f1 = 1
        else:
            precision = intersection_with_lcs / len(predicted) if predicted else 0
            recall = intersection_with_lcs / len(expected) if expected else 0
            if tolerate_additionally_predicted and not only_in_expected:
                recall = 1
            f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0 if expected or predicted else 1
        return precision, recall, f1
    else:
        if not expected and not predicted:
            return 1, 1, 1
        tp0 = 0
        for i in range(min(len(expected), len(predicted))):
            if expected[i] == predicted[i]:
                tp0 += 1
            else:
                if lcs_threshold:
                    ilcs_rate = lcs_rate(expected[i], predicted[i])
                    if ilcs_rate >= lcs_threshold:
                        tp0 += ilcs_rate
        i = 0
        j = 0
        tp1 = 0
        if tolerate_additionally_predicted:
            while i < len(expected) and i < len(predicted):
                while i+j < len(expected) and i+j < len(predicted):
                    if expected[i] == predicted[i+j]:
                        tp1 += 1
                        break
                    if lcs_threshold:
                        ilcs_rate = lcs_rate(expected[i], predicted[i+j])
                        if ilcs_rate >= lcs_threshold:
                            tp1 += ilcs_rate
                            break
                    j += 1
                i += 1
        tp = max(tp0, tp1)
        precision = tp / len(predicted) if predicted else 0
        recall = tp / len(expected) if expected else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        return precision, recall, f1



def calc_statistics(saved_queries, data_type=DataType.ENTITY, try_heuristic_parse=True, **kwargs):
    K_EXPECT_EMPTY = '(Expected) Empty'
    K_EXPECT_NON_EMPTY = '(Expected) Non-empty'
    K_PREDICT_EMPTY = '(Predicted) Empty'
    K_PREDICT_NON_EMPTY = '(Predicted) Non-empty'

    result_score_list = []
    addition_scoring = {
        K_EXPECT_NON_EMPTY: [],
        K_EXPECT_EMPTY: [],
        K_PREDICT_NON_EMPTY: [],
        K_PREDICT_EMPTY: [],
    }

    failed = {}
    for i, (model_output, correct_output) in enumerate([(query['output'], query['correct_output']) for query in saved_queries]):
        try:
            model_output_parsed = json.loads(model_output)
        except json.JSONDecodeError as e:
            really_failed = True
            if try_heuristic_parse:
                try:
                    _, model_output_parsed = try_parse_json_object(model_output)
                    if model_output_parsed is not None:
                        really_failed = False
                except SyntaxError as e:
                    pass
            if really_failed:
                failed[i] = (model_output, correct_output)
                continue
        if try_heuristic_parse:
            model_output_parsed = heuristic_extract_entities(model_output_parsed, data_type=data_type)
        correct_output_parsed = json.loads(correct_output)
        try:
            result_score = precision_accuracy_f1(correct_output_parsed, model_output_parsed, data_type=data_type, **kwargs)
        except TypeError as e:
            failed[i] = (model_output, correct_output)
            continue
        result_score_list.append(result_score)
        if correct_output_parsed:
            addition_scoring[K_EXPECT_NON_EMPTY].append(result_score)
        else:
            addition_scoring[K_EXPECT_EMPTY].append(result_score)
        if model_output_parsed:
            addition_scoring[K_PREDICT_NON_EMPTY].append(result_score)
        else:
            addition_scoring[K_PREDICT_EMPTY].append(result_score)

    return result_score_list, addition_scoring, failed


def calc_and_print_statistics(desc, saved_queries, data_type=DataType.ENTITY, try_heuristic_parse=True, lcs_threshold=None, tolerate_additionally_predicted=None, ignore_order=True):
    result_score_list, addition_scoring, failed = calc_statistics(saved_queries, data_type=data_type, try_heuristic_parse=try_heuristic_parse, lcs_threshold=lcs_threshold, tolerate_additionally_predicted=tolerate_additionally_predicted, ignore_order=ignore_order)

    print(f"Stat for eval with desc: {desc}")
    print(f"  {len(result_score_list)} valid datapoints, avg. precission, recall, f1:", np.mean(result_score_list, axis=0))
    for k, score_list in addition_scoring.items():
        if not score_list: continue
        print(f"  {len(score_list)} datapoints for {k}, with avg. precission, recall, f1:", np.mean(score_list, axis=0))
    # print(f"  {len(non_empty_result_score_list)} (ought to be) non-empty datapoints, avg. precission, recall, f1:", np.mean(non_empty_result_score_list, axis=0))
    # print(f"  {len(empty_result_score_list)} (ought to be) empty datapoints, avg. precission, recall, f1:", np.mean(empty_result_score_list, axis=0))
    print(f"  {len(failed)} datapoints are not valid (e.g. not JSON; malformed model output)")
    print("  ", end=''), pprint(failed)