import json
import numpy as np
from pprint import pprint
import pylcs
from .external.json_parse import try_parse_json_object


def precision_accuracy_f1(expected, predicted, lcs_threshold=None):
    expected = set(expected)
    predicted = set(predicted)

    intersection = expected.intersection(predicted)
    intersection_with_lcs = len(intersection)
    if lcs_threshold is not None:
        only_in_expected = list(expected - predicted)
        only_in_predicted = list(predicted - expected)
        used = []  # Greedy. Probably underestimating, but efficient and mostly near-correct.
        for e1 in only_in_expected:
            maximum_lcs_length = 0
            maximum_lcs_index = -1
            for i, e2 in enumerate(only_in_predicted):
                if i in used: continue
                lcs_length = pylcs.lcs_sequence_length(e1, e2)
                if lcs_length > maximum_lcs_length:
                    maximum_lcs_length = lcs_length
                    maximum_lcs_index = i
            maximum_lcs_rate = maximum_lcs_length / len(e1) if e1 else 0  # Similar to precision
            if maximum_lcs_rate >= lcs_threshold:
                intersection_with_lcs += maximum_lcs_rate
                used.append(maximum_lcs_index)

    precision = intersection_with_lcs / len(predicted) if predicted else 0 if expected else 1
    recall = intersection_with_lcs / len(expected) if expected else 0 if predicted else 1
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0 if expected or predicted else 1
    return precision, recall, f1
    # return sklm.precision_recall_fscore_support(expected, predicted)[:3]


def heuristic_extract_data_entities(parsed_model_output):
    extracted_output = []
    for obj in parsed_model_output:
        if isinstance(obj, str):
            extracted_output.append(obj)
        else:
            if 'context_type' in obj and 'data_entity' in obj:  # gpt-4o-mini-2024-07-18
                extracted_output.append(obj['data_entity'])
            elif 'context' in obj and 'data_entity' in obj:  # gpt-4o-mini-2024-07-18
                extracted_output.append(obj['data_entity'])
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


def calc_statistics(saved_queries, try_heuristic_parse=True, lcs_threshold=None):
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
            model_output_parsed = heuristic_extract_data_entities(model_output_parsed)
        correct_output_parsed = json.loads(correct_output)
        try:
            result_score = precision_accuracy_f1(correct_output_parsed, model_output_parsed, lcs_threshold=lcs_threshold)
        except TypeError as e:
            failed[i] = (model_output, correct_output)
            continue
        result_score_list.append(result_score)
        if correct_output_parsed:
            non_empty_result_score_list.append(result_score)
        else:
            empty_result_score_list.append(result_score)

    return result_score_list, non_empty_result_score_list, empty_result_score_list, failed


def calc_and_print_statistics(desc, saved_queries, try_heuristic_parse=True, lcs_threshold=None):
    result_score_list, non_empty_result_score_list, empty_result_score_list, failed = calc_statistics(saved_queries, try_heuristic_parse=try_heuristic_parse, lcs_threshold=lcs_threshold)

    print(f"Stat for eval with desc: {desc}")
    print(f"  {len(result_score_list)} valid datapoints, avg. precission, recall, f1:", np.mean(result_score_list, axis=0))
    print(f"  {len(non_empty_result_score_list)} (ought to be) non-empty datapoints, avg. precission, recall, f1:", np.mean(non_empty_result_score_list, axis=0))
    print(f"  {len(empty_result_score_list)} (ought to be) empty datapoints, avg. precission, recall, f1:", np.mean(empty_result_score_list, axis=0))
    print(f"  {len(failed)} datapoints are not valid (e.g. not JSON; malformed model output)")
    print("  ", end=''), pprint(failed)