import json
import numpy as np
from pprint import pprint
from .external.json_parse import try_parse_json_object


def precision_accuracy_f1(expected, predicted):
    expected = set(expected)
    predicted = set(predicted)
    precision = len(expected.intersection(predicted)) / len(predicted) if predicted else 0 if expected else 1
    recall = len(expected.intersection(predicted)) / len(expected) if expected else 0 if predicted else 1
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0 if expected or predicted else 1
    return precision, recall, f1
    # return sklm.precision_recall_fscore_support(expected, predicted)[:3]


def calc_statistics(saved_queries, try_heuristic_parse=True):
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
        correct_output_parsed = json.loads(correct_output)
        try:
            result_score = precision_accuracy_f1(correct_output_parsed, model_output_parsed)
        except TypeError as e:
            failed[i] = (model_output, correct_output)
            continue
        result_score_list.append(result_score)
        if correct_output_parsed:
            non_empty_result_score_list.append(result_score)
        else:
            empty_result_score_list.append(result_score)

    return result_score_list, non_empty_result_score_list, empty_result_score_list, failed


def calc_and_print_statistics(desc, saved_queries, try_heuristic_parse=True):
    result_score_list, non_empty_result_score_list, empty_result_score_list, failed = calc_statistics(saved_queries, try_heuristic_parse=try_heuristic_parse)

    print(f"Stat for eval with desc: {desc}")
    print(f"  {len(result_score_list)} valid datapoints, avg. precission, recall, f1:", np.mean(result_score_list, axis=0))
    print(f"  {len(non_empty_result_score_list)} (ought to be) non-empty datapoints, avg. precission, recall, f1:", np.mean(non_empty_result_score_list, axis=0))
    print(f"  {len(empty_result_score_list)} (ought to be) empty datapoints, avg. precission, recall, f1:", np.mean(empty_result_score_list, axis=0))
    print(f"  {len(failed)} datapoints are not valid (e.g. not JSON; malformed model output)")
    print("  ", end=''), pprint(failed)