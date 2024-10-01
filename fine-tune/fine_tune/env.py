'''
Load environmental information, data and settings
'''

import csv
from dotenv import load_dotenv
import os
from ppa_commons.env_helper import get_entity_category_definitions, get_entity_category_hierarchy


load_dotenv()


BRAT_DATA_PATH = os.environ['BRAT_DATA_PATH']

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

