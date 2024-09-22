import json
import numpy as np
from pprint import pprint
from pydantic import BaseModel, Field
import pylcs
from typing import Optional
from .external.json_parse import try_parse_json_object


def lcs_rate(a, b):
    if isinstance(a, str) and isinstance(b, str):
        rate = pylcs.lcs_sequence_length(a, b) / len(a) if a else 0  # Similar to precision
    else:
        rate = a.lcs_rate(b)
    if rate > 1:
        rate = 1
    return rate


T_ENTITY = 'entity'
T_ACTION = 'action'
T_PROTECTION_METHOD = 'protection_method'
T_PARTY = 'party'
T_RELATION = 'relation'


class DataPoint(BaseModel):
    class Config:
        frozen = True


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


_data_type_to_class = {
    T_ACTION: ActionDataPoint,
    T_PROTECTION_METHOD: ProtectionMethodDataPoint,
    T_PARTY: PartyDataPoint,
    T_RELATION: RelationDataPoint,
}


def precision_accuracy_f1(expected, predicted, data_type=T_ENTITY, lcs_threshold=None, tolerate_additionally_predicted=None):
    if data_type == T_PARTY and tolerate_additionally_predicted is None:
        tolerate_additional_in_predicted = True
    if data_type == T_ENTITY:
        expected = set(expected)
        predicted = set(predicted)
    elif data_type == T_ACTION:
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
                if lcs_threshold == -1 and data_type == T_ENTITY:
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
    # return sklm.precision_recall_fscore_support(expected, predicted)[:3]


def heuristic_extract_data_entities(parsed_model_output, data_type=T_ENTITY):
    if data_type != T_ENTITY:  # Not all data types should/can be heuristic-extracted
        return parsed_model_output
    extracted_output = []
    for obj in parsed_model_output:
        if isinstance(obj, str):
            extracted_output.append(obj)
        else:
            if 'context_type' in obj and 'data_entity' in obj:  # gpt-4o-mini-2024-07-18
                extracted_output.append(obj['data_entity'])
            elif 'context' in obj and 'data_entity' in obj:  # gpt-4o-mini-2024-07-18
                extracted_output.append(obj['data_entity'])
            elif 'context' in obj and 'purpose' in obj:  # gpt-4o
                extracted_output.append(obj['purpose'])
            elif 'type' in obj and 'text' in obj:  # gpt-4o
                extracted_output.append(obj['text'])
            elif 'text' in obj:
                extracted_output.append(obj['text'])
            elif 'type' in obj and 'dataEntity' in obj:  # Spark 4.0 Ultra
                extracted_output.append(obj['dataEntity'])
            elif 'context' in obj and 'dataEntity' in obj:  # Spark 4.0 Ultra
                extracted_output.append(obj['dataEntity'])
            elif 'contextType' in obj and 'dataEntity' in obj:  # Spark 4.0 Ultra
                extracted_output.append(obj['dataEntity'])
            elif 'type' in obj and 'data' in obj:  # Spark 4.0 Ultra
                extracted_output.append(obj['data'])
            elif 'type' in obj and 'entity' in obj:  # Spark 4.0 Ultra
                extracted_output.append(obj['entity'])
            elif 'context' in obj and 'entity' in obj:  # Spark 4.0 Ultra
                extracted_output.append(obj['entity'])
            else:
                extracted_output.append(obj)
    return extracted_output


def calc_statistics(saved_queries, data_type=T_ENTITY, try_heuristic_parse=True, lcs_threshold=None, tolerate_additionally_predicted=None):
    result_score_list = []
    empty_result_score_list = []
    non_empty_result_score_list = []

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
            model_output_parsed = heuristic_extract_data_entities(model_output_parsed, data_type=data_type)
        correct_output_parsed = json.loads(correct_output)
        try:
            result_score = precision_accuracy_f1(correct_output_parsed, model_output_parsed, data_type=data_type, lcs_threshold=lcs_threshold, tolerate_additionally_predicted=tolerate_additionally_predicted)
        except TypeError as e:
            failed[i] = (model_output, correct_output)
            continue
        result_score_list.append(result_score)
        if correct_output_parsed:
            non_empty_result_score_list.append(result_score)
        else:
            empty_result_score_list.append(result_score)

    return result_score_list, non_empty_result_score_list, empty_result_score_list, failed


def calc_and_print_statistics(desc, saved_queries, data_type=T_ENTITY, try_heuristic_parse=True, lcs_threshold=None, tolerate_additionally_predicted=None):
    result_score_list, non_empty_result_score_list, empty_result_score_list, failed = calc_statistics(saved_queries, data_type=data_type, try_heuristic_parse=try_heuristic_parse, lcs_threshold=lcs_threshold, tolerate_additionally_predicted=tolerate_additionally_predicted)

    print(f"Stat for eval with desc: {desc}")
    print(f"  {len(result_score_list)} valid datapoints, avg. precission, recall, f1:", np.mean(result_score_list, axis=0))
    print(f"  {len(non_empty_result_score_list)} (ought to be) non-empty datapoints, avg. precission, recall, f1:", np.mean(non_empty_result_score_list, axis=0))
    print(f"  {len(empty_result_score_list)} (ought to be) empty datapoints, avg. precission, recall, f1:", np.mean(empty_result_score_list, axis=0))
    print(f"  {len(failed)} datapoints are not valid (e.g. not JSON; malformed model output)")
    print("  ", end=''), pprint(failed)