from collections import defaultdict
from .data_model import (
    SegmentedDataPractice,
    DataPractice,
    DataCollectionUse,
    DataSharingDisclosure,
    DataStorageRetention,
    DataSecurityProtection,
    DataEntity,
    PurposeEntity,
    PartyEntity,
    Location,
    Duration,
    SecurityThreat,
    ProtectionMethod,
)
from . import hierarchy_helper as hh


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


def calc_practice_field_count(segmented_practices: list[SegmentedDataPractice]):
    field_count: dict[DataPractice, dict[str, list[int]]] = {
        DataCollectionUse: defaultdict(list),
        DataSharingDisclosure: defaultdict(list),
        DataStorageRetention: defaultdict(list),
        DataSecurityProtection: defaultdict(list),
    }

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


def calc_practice_entity_count(segmented_practices: list[SegmentedDataPractice]):
    '''
    Count the number of occurances of each different type of entity across all practices
    '''
    entity_count = defaultdict(lambda: defaultdict(int))
    for segmented_practice in segmented_practices:
        for practice in segmented_practice.practices:
            for field in fields:
                if hasattr(practice, field):
                    field_v = getattr(practice, field)
                    if isinstance(field_v, list):
                        for entity in getattr(practice, field):
                            internal_count = entity_count[entity.__class__]
                            if isinstance(entity, (DataEntity, PurposeEntity, PartyEntity)):
                                internal_count[entity.category] += 1
                            else:
                                internal_count[entity.text] += 1
    return dict({k: dict(v) for k,v in entity_count.items()})


def calc_data_and_purpose_entity_count_with_hierarchy(segmented_practices: list[SegmentedDataPractice], accumulate_to_parent: bool = True):
    entity_path_list = {
        DataEntity: [],
        PurposeEntity: [],
    }
    for segmented_practice in segmented_practices:
        for practice in segmented_practice.practices:
            for field in fields:
                if hasattr(practice, field):
                    field_v = getattr(practice, field)
                    if isinstance(field_v, list):
                        for entity in field_v:
                            if isinstance(entity, (DataEntity)):
                                path = hh.get_path_to_data_category(entity.category)
                                entity_path_list[DataEntity].append(path)
                            elif isinstance(entity, (PurposeEntity)):
                                path = hh.get_path_to_purpose(entity.category)
                                entity_path_list[PurposeEntity].append(path)
    node_with_count = {}
    for entity_type, path_list in entity_path_list.items():
        node_with_count[entity_type] = {}
        for paths_of_entity in path_list:
            current_node = paths_of_entity[0][-1]
            all_nodes = set()
            for path in paths_of_entity:
                all_nodes.update(path)
            for node in all_nodes:
                if node not in node_with_count[entity_type]:
                    node_with_count[entity_type][node] = 0
                if accumulate_to_parent:
                    node_with_count[entity_type][node] += 1
            if not accumulate_to_parent:
                node_with_count[entity_type][current_node] += 1
    return node_with_count
