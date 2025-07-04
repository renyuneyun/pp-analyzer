'''
Copied from `fine-tune`. Nothing changed. Probably most fields are unnecessary as only the category definitions and hierarchy are useful
'''

import csv
from dotenv import load_dotenv
import os


load_dotenv()


def get_entity_category_hierarchy(entity_category_hierarchy_file):
    '''
    The entity category hierarchy contains multiple lines, each representing one category; the number of indents (`\t`) at the beginning of a line indicates the level of the category.
    There will be no cycles. One category may belong to multiple parental-categories.
    This function returns the category hierarchy as a nested dictionary, where the key is the category name, and the value is a list of subcategories.
    '''
    with open(entity_category_hierarchy_file) as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    res = {}
    stack = []
    for line in lines:
        level = line.count('\t')
        name = line.strip()
        if level > len(stack):
            raise ValueError("Invalid hierarchy with exceptional indentation")
        l = res
        for i in range(level):
            l = l[stack[i]]
        l[name] = {}
        stack = stack[:level] + [name]

    return res


def get_entity_category_definitions(entity_category_definition_file):
    '''
    The entity category definition is a CSV file with two columns: category, definition.
    This function returns the category definitions as a dictionary, where the key is the category name, and the value is the definition.
    '''
    with open(entity_category_definition_file) as f:
        reader = csv.reader(f)
        next(reader)
        return {line[0]: line[1] for line in reader}


F_DATA_CATEGORY_HIERARCHY = os.environ.get("DATA_CATEGORY_HIERARCHY")
F_DATA_CATEGORY_DEFINITION = os.environ.get("DATA_CATEGORY_DEFINITION")
F_PURPOSE_CATEGORY_HIERARCHY = os.environ.get("PURPOSE_CATEGORY_HIERARCHY")
F_PURPOSE_CATEGORY_DEFINITION = os.environ.get("PURPOSE_CATEGORY_DEFINITION")

if F_DATA_CATEGORY_DEFINITION:
    with open(F_DATA_CATEGORY_DEFINITION, "r") as f:
        _data_category_definitions_text = f.read()
    _data_category_definitions = get_entity_category_definitions(F_DATA_CATEGORY_DEFINITION)

if F_DATA_CATEGORY_HIERARCHY:
    with open(F_DATA_CATEGORY_HIERARCHY, "r") as f:
        _data_category_hierarchy_text = f.read()
    _data_category_hierarchy = get_entity_category_hierarchy(F_DATA_CATEGORY_HIERARCHY)

if F_PURPOSE_CATEGORY_DEFINITION:
    with open(F_PURPOSE_CATEGORY_DEFINITION, "r") as f:
        _purpose_category_definitions_text = f.read()
    _purpose_category_definitions = get_entity_category_definitions(F_PURPOSE_CATEGORY_DEFINITION)

if F_PURPOSE_CATEGORY_HIERARCHY:
    with open(F_PURPOSE_CATEGORY_HIERARCHY, "r") as f:
        _purpose_category_hierarchy_text = f.read()
    _purpose_category_hierarchy = get_entity_category_hierarchy(F_PURPOSE_CATEGORY_HIERARCHY)

PROTECTION_METHODS = [
    'general-safeguard-method',
	'User-authentication',
	'encryptions',
	'Access-limitation',
	'Protection-other',
]

PARTY_ENTITIES = [
    'First-party-entity',
    'Third-party-entity',
    'Third-party-name',
    'User',
]

