from collections import defaultdict
from .data_model import (
    SegmentedDataPractice,
    DataPractice,
    DataCollectionUse,
    DataSharingDisclosure,
    DataStorageRetention,
    DataSecurityProtection,
)

def calc_practice_field_count(segmented_practices: list[SegmentedDataPractice]):
    field_count: dict[DataPractice, dict[str, list[int]]] = {
        DataCollectionUse: defaultdict(list),
        DataSharingDisclosure: defaultdict(list),
        DataStorageRetention: defaultdict(list),
        DataSecurityProtection: defaultdict(list),
    }

    fields = [
        'data_collector',
        'data_provider',
        'data_collected',
        'purpose',
        'data_receiver',
        'data_sharer',
        'data_shared',
        'data_holder',
        'data_retained',
        'storage_place',
        'retention_period',
        'data_protector',
        'data_protected',
        'protect_against',
        'protection_method',
    ]

    for segmented_practice in segmented_practices:
        for practice in segmented_practice.practices:
            tgt = field_count[practice.__class__]
            for field in fields:
                if hasattr(practice, field):
                    tgt[field].append(len(getattr(practice, field, [])))

    return field_count


def calc_count_stats(field_count, quiet=False):
    stat_tasks = {
        'exists': lambda field, counts, number_total: sum([int(bool(i)) for i in counts]) / number_of_item,
        'average count': lambda field, counts, number_total: sum(counts) / len(counts),
        'num zeros': lambda field, counts, number_total: len([i for i in counts if i == 0]),
        'num > 1': lambda field, counts, number_total: len([i for i in counts if i > 1]),
    }

    res = {}
    for k, v in field_count.items():
        class_name = k.__name__
        number_of_item = None
        stat_results = {field: {} for field in v.keys()}
        for field, counts in v.items():
            if number_of_item is None:
                number_of_item = len(counts)
            else:
                assert number_of_item == len(counts), 'Inconsistent field count recorded'
            for tk, tfn in stat_tasks.items():
                stat_results[field][tk] = tfn(field, counts, number_of_item)
        res[class_name] = (number_of_item, stat_results)
        if not quiet:
            print(f"{class_name:25} #{number_of_item}")
            for field in v.keys():
                print(f"""  {field:20}: {" :: ".join(f"{k}: {(f'{v:.3f}' if isinstance(v, float) else f'{v}')}" for k, v in stat_results[field].items())}""")
    return res
