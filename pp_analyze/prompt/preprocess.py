from .original import (
    SYSTEM_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION as _SYSTEM_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION,

)

from .env import (
    _data_category_hierarchy_text,
    _data_category_definitions_text,
)


SYSTEM_MESSAGE_DATA_ENTITY_CLASSIFICATION = _SYSTEM_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION.format(
                                                hierarchy=_data_category_hierarchy_text,
                                                definitions=_data_category_definitions_text,
                                            )