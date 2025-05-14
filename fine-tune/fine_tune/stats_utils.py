import json
import numpy as np
from pprint import pprint
from pydantic import BaseModel, Field, ValidationError
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


class SubsumeRelationDataPoint(DataPoint):
    subsuming: str
    subsumed: str

    def lcs_rate(self, o):
        return self.subsumed == o.subsumed and self.subsuming == o.subsuming
        # return self.subsumed == o.subsuming and self.subsuming == o.subsumed  # For testing only: what if the prediction is reversed?


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
    DataType.SUBSUMPTION: SubsumeRelationDataPoint,
    DataType.RETENTION_DETAILS: RetentionDetailsDataPoint,
}


def precision_recall_f1(tp, n_expected, n_predicted, tolerate_additionally_predicted=None):
    if n_expected == 0 and n_predicted == 0:
        return 1, 1, 1
    precision = tp / n_predicted if n_predicted else 0
    recall = tp / n_expected if n_expected else 0
    if tolerate_additionally_predicted and n_expected - tp == 0:
        recall = 1
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return precision, recall, f1


def calc_precision_recall_f1(expected, predicted, data_type=DataType.ENTITY, lcs_threshold=None, tolerate_additionally_predicted=None, ignore_order=True, check_contains=False, **kwargs):
    '''
    @param check_contains: bool, whether to check if the predicted output contains the expected output. If True, each predicted output is a list, and this function will check if the expected output is a subset of the predicted output. If False, the expected output and predicted output are compared element-wise.
    '''

    if ignore_order:
        expected = set(expected)
        predicted = set(predicted)

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

        precision, recall, f1 = precision_recall_f1(intersection_with_lcs, len(expected), len(predicted), tolerate_additionally_predicted=tolerate_additionally_predicted)
        return precision, recall, f1
    else:
        tp0 = 0
        for i in range(min(len(expected), len(predicted))):
            if check_contains:
                if expected[i] in predicted[i]:
                    tp0 += 1
            else:
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
        precision, recall, f1 = precision_recall_f1(tp, len(expected), len(predicted), tolerate_additionally_predicted=tolerate_additionally_predicted)
        return precision, recall, f1


def calc_stats_item(expected, predicted, data_type=DataType.ENTITY, lcs_threshold=None, tolerate_additionally_predicted=None, ignore_order=True, **kwargs):

    if data_type == DataType.PARTY and tolerate_additionally_predicted is None:
        tolerate_additionally_predicted = True

    if data_type == DataType.ENTITY:
        pass
    elif data_type == DataType.ACTION:
        if isinstance(expected, dict):
            expected = [expected]
        try:
            expected = [ActionDataPoint(**obj) for obj in expected]
            predicted = [ActionDataPoint(**obj) for obj in predicted]
        except Exception as e:
            # print(f"Error in parsing action data point: {e};\n  expected: {expected};\n  predicted: {predicted}")
            raise e
    elif data_type in _data_type_to_class:
        cls = _data_type_to_class[data_type]
        expected = [cls(**obj) for obj in expected]
        predicted = [cls(**obj) for obj in predicted]
    else:
        raise ValueError(f"Unrecognised data_type: {data_type}")

    prec, acc, f1 = calc_precision_recall_f1(expected, predicted, data_type=data_type, lcs_threshold=lcs_threshold, tolerate_additionally_predicted=tolerate_additionally_predicted, ignore_order=ignore_order, **kwargs)

    return prec, acc, f1


def calc_statistics(saved_queries, data_type=DataType.ENTITY, try_heuristic_parse=True, already_parsed=False, **kwargs):
    '''
    @param saved_queries: list of dict, each dict contains 'output' and 'correct_output'. The 'output' and 'correct_output' are either JSON string or already parsed object.
    @param data_type: DataType, the type of data to be evaluated.
    @param try_heuristic_parse: bool, whether to try to extract entities from the output through heuristics found from existing outputs.
    @param already_parsed: bool, whether the output and correct_output (of save_queries) are already parsed objects.
    @param kwargs: other arguments to be passed to calc_stats_item.
    '''

    K_EXPECT_EMPTY = '(Expected) Empty'
    K_EXPECT_NON_EMPTY = '(Expected) Non-empty'
    K_PREDICT_EMPTY = '(Predicted) Empty'
    K_PREDICT_NON_EMPTY = '(Predicted) Non-empty'
    K_EITHER_EMPTY = '(Either) Empty'
    K_EITHER_NON_EMPTY = '(Either) Non-empty'

    result_score_list = []
    addition_scoring = {
        K_EXPECT_NON_EMPTY: [],
        K_EXPECT_EMPTY: [],
        K_PREDICT_NON_EMPTY: [],
        K_PREDICT_EMPTY: [],
        K_EITHER_NON_EMPTY: [],
        K_EITHER_EMPTY: [],
    }

    def add_scoring(key, score):
        addition_scoring[key].append(score)

    failed = {}
    for i, (model_output, correct_output) in enumerate([(query['output'], query['correct_output']) for query in saved_queries]):
        if already_parsed:
            model_output_parsed = model_output
        else:
            try:
                model_output_parsed = json.loads(model_output)
            except (json.JSONDecodeError, TypeError) as e:
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
        if already_parsed:
            correct_output_parsed = correct_output
        else:
            correct_output_parsed = json.loads(correct_output)
        try:
            result_score = calc_stats_item(correct_output_parsed, model_output_parsed, data_type=data_type, **kwargs)
        except (TypeError, ValidationError) as e:
            failed[i] = (model_output, correct_output)
            continue
        result_score_list.append(result_score)
        if correct_output_parsed:
            add_scoring(K_EXPECT_NON_EMPTY, result_score)
            add_scoring(K_EITHER_NON_EMPTY, result_score)
        else:
            add_scoring(K_EXPECT_EMPTY, result_score)
            add_scoring(K_EITHER_EMPTY, result_score)

        if model_output_parsed:
            add_scoring(K_PREDICT_NON_EMPTY, result_score)
            if not correct_output_parsed:  # Haven't been added to K_EITHER_NON_EMPTY; otherwise it's already there so no need to add again
                add_scoring(K_EITHER_NON_EMPTY, result_score)
        else:
            add_scoring(K_PREDICT_EMPTY, result_score)
            if correct_output_parsed:  # Haven't been added to K_EITHER_EMPTY; otherwise it's already there so no need to add again
                add_scoring(K_EITHER_EMPTY, result_score)

    return result_score_list, addition_scoring, failed


def calc_group(result_score_list):
    precision_recall_f1_list = [item[:3] for item in result_score_list]
    return np.mean(precision_recall_f1_list, axis=0)


def calc_and_print_statistics(desc, saved_queries, data_type=DataType.ENTITY, try_heuristic_parse=True, already_parsed=False, lcs_threshold=None, tolerate_additionally_predicted=None, ignore_order=True, check_contains=False):
    result_score_list, addition_scoring, failed = calc_statistics(saved_queries, data_type=data_type, try_heuristic_parse=try_heuristic_parse, already_parsed=already_parsed, lcs_threshold=lcs_threshold, tolerate_additionally_predicted=tolerate_additionally_predicted, ignore_order=ignore_order, check_contains=check_contains)

    print(f"Stat for eval with desc: {desc}")
    print(f"  {len(result_score_list)} valid datapoints, avg. precission, recall, f1:", calc_group(result_score_list))
    for k, score_list in addition_scoring.items():
        if not score_list: continue
        print(f"  {len(score_list)} datapoints for {k}, with avg. precission, recall, f1:", calc_group(score_list))
    # print(f"  {len(non_empty_result_score_list)} (ought to be) non-empty datapoints, avg. precission, recall, f1:", np.mean(non_empty_result_score_list, axis=0))
    # print(f"  {len(empty_result_score_list)} (ought to be) empty datapoints, avg. precission, recall, f1:", np.mean(empty_result_score_list, axis=0))
    print(f"  {len(failed)} datapoints are not valid (e.g. not JSON; malformed model output)")
    print("  ", end=''), pprint(failed)