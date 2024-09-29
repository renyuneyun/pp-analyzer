T_ENTITY = 'entity'
T_ENTITY_WITH_ACTION = 'entity_with_action'
T_ACTION = 'action'
T_PROTECTION_METHOD = 'protection_method'
T_PARTY = 'party'
T_RELATION = 'relation'


def heuristic_extract_entities(parsed_model_output, data_type=T_ENTITY):
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