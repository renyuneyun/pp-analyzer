from enum import Enum

class QueryCategory(Enum):
    DATA_ENTITY = "data_entity"
    DATA_CLASSIFICATION = "data_classification"
    PURPOSE_ENTITY = "purpose_entity"
    PURPOSE_CLASSIFICATION = "purpose_classification"
    PARTY_RECOGNITION = "party_recognition"
    DATA_PRACTICE = "data_practice_action"
    RELATION_RECOGNITION = "relation_recognition"


T_OVERRIDE_CACHE = set[QueryCategory]
PARAM_OVERRIDE_CACHE = T_OVERRIDE_CACHE | bool | None


class MalformedDataError(Exception):
    '''Raised when the data is not in the expected format'''
    pass


class UnexpectedEntryError(MalformedDataError):
    '''Raised when an unexpected entry is found in the data, such as a missing field or unexpected value in the field'''
    pass
