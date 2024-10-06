from dotenv import load_dotenv
import json
import os
from rdflib import URIRef
from ppa_commons import get_entity_category_hierarchy


load_dotenv()


def get_purpose_hierarchy():
    purpose_hierarchy_file = os.getenv("PURPOSE_CATEGORY_HIERARCHY")
    purpose_hierarchy = get_entity_category_hierarchy(purpose_hierarchy_file)
    return purpose_hierarchy


def get_data_category_hierarchy():
    data_category_hierarchy_file = os.getenv("DATA_CATEGORY_HIERARCHY")
    data_category_hierarchy = get_entity_category_hierarchy(data_category_hierarchy_file)
    return data_category_hierarchy


def get_path_to_node(node: str, hierarchy: dict) -> list[str]:
    """
    Get the path(s) to a node in the hierarchy.
    """
    paths = []
    for parent, children in hierarchy.items():
        if parent == node:
            paths.append([parent])
        else:
            for path in get_path_to_node(node, children):
                paths.append([parent] + path)
    return paths


def map_entity_category_to_level(category: str, hierarchy: dict, level: int = 1):
    """
    Map a (deep) entity category class to a higher level category class, as specified in DPV.
    level 0: top level class (e.g. Purpose)

    If multi-inheritance exists, prefer the deepest match.
    If the category is not found in the hierarchy, return the category itself.
    The `category` must be the key type of the hierarchy.
    """
    if level == -1:
        return category
    paths = get_path_to_node(category, hierarchy)
    if not paths:
        return category
    longest_path = []
    for path in paths:
        if len(path) > len(longest_path):
            longest_path = path
    if len(longest_path) > level:
        return longest_path[level]
    else:
        return longest_path[-1]


def map_category_uri_to_level(category_uri: URIRef, hierarchy: dict, level: int = 1):
    category_name = category_uri.split("#")[-1]
    mapped_category_name = map_entity_category_to_level(category_name, hierarchy, level)
    if '#' in category_uri:
        prefix = category_uri.split("#")[0] + '#'
    else:
        prefix = ''
    return URIRef(prefix + mapped_category_name)


def map_purpose_to_level(purpose: URIRef, level: int = 1):
    """
    Map a (deep) purpose class to a higher level purpose class, as specified in DPV.
    level 0: top level purpose class (Purpose)

    If multi-inheritance exists, prefer the deepest match.
    """
    hierarchy = get_purpose_hierarchy()
    return map_category_uri_to_level(purpose, hierarchy, level)


def map_data_category_to_level(data_category: str, level: int = 1):
    """
    Map a (deep) data category class to a higher level data category class, as specified in DPV.
    level 0: top level data category class (Data)

    If multi-inheritance exists, prefer the deepest match.
    """
    hierarchy = get_data_category_hierarchy()
    return map_entity_category_to_level(data_category, hierarchy, level)


def get_path_to_purpose(purpose: URIRef):
    return get_path_to_node(purpose, get_purpose_hierarchy())

def get_path_to_data_category(data_category: str):
    return get_path_to_node(data_category, get_data_category_hierarchy())


def lift_category_to_target(category: str, targets: list[str], hierarchy: dict) -> str:
    """
    Lift a category to match the target categories -- if it is a subclass of any of them, change it to that target. If multiple matches are found, the deepest match is chosen.
    If the category is not a subclass of any of the target categories, return the category itself. Thus it's safe to apply this function without checking the subclass relationship.
    Assumes that the category is in the hierarchy.
    """
    paths = get_path_to_node(category, hierarchy)
    if not paths:
        return category
    longest_path = []
    for path in paths:
        if len(path) > len(longest_path):
            longest_path = path
    for elem in reversed(longest_path):
        if elem in targets:
            return elem
    return category


def lift_purpose_to_target(purpose: str, targets: list[str]):
    hierarchy = get_purpose_hierarchy()
    return lift_category_to_target(purpose, targets, hierarchy)


def lift_data_category_to_target(data_category: str, targets: list[str]):
    hierarchy = get_data_category_hierarchy()
    return lift_category_to_target(data_category, targets, hierarchy)
