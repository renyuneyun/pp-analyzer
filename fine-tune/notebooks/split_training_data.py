import numpy as np
from fine_tune import utils


def has_no_entities(segment):
    return not segment["entities"]


def simple_split(data_entities):
    NUM_TRAIN_HAS_ENTITY = 20
    NUM_TRAIN_NO_ENTITY = 10
    NUM_VAL_HAS_ENTITY = 3
    NUM_VAL_NO_ENTITY = 2

    empty_entity_indices = [i for i, segment in enumerate(data_entities) if has_no_entities(segment)]

    training_set_indices = []
    validation_set_indices = []
    for i, segment in enumerate(data_entities):
        if not has_no_entities(segment):
            if len(training_set_indices) < 20:
                training_set_indices.append(i)
            elif len(validation_set_indices) < 3:
                validation_set_indices.append(i)

    for i in empty_entity_indices:
        if len(training_set_indices) < 30:
            training_set_indices.append(i)
        elif len(validation_set_indices) < 5:
            validation_set_indices.append(i)

    return training_set_indices, validation_set_indices


def better_split(data_entities, num_split=[10, 30, 2, 6]):
    NUM_TRAIN_HAS_ENTITY, NUM_TRAIN_NO_ENTITY, NUM_VAL_HAS_ENTITY, NUM_VAL_NO_ENTITY = num_split

    empty_entity_indices = [i for i, segment in enumerate(data_entities) if has_no_entities(segment)]
    non_empty_entity_indices = [i for i, segment in enumerate(data_entities) if not has_no_entities(segment)]

    training_set_indices = []
    validation_set_indices = []

    indices, idx = utils.evenly_get(empty_entity_indices, NUM_TRAIN_NO_ENTITY)
    training_set_indices += indices.tolist()
    empty_entity_indices_remaining = np.delete(empty_entity_indices, idx)
    indices, idx = utils.evenly_get(empty_entity_indices_remaining, NUM_VAL_NO_ENTITY)
    validation_set_indices += indices.tolist()
    indices, idx = utils.evenly_get(non_empty_entity_indices, NUM_TRAIN_HAS_ENTITY)
    training_set_indices += indices.tolist()
    non_empty_entity_indices_remaining = np.delete(non_empty_entity_indices, idx)
    indices, idx = utils.evenly_get(non_empty_entity_indices_remaining, NUM_VAL_HAS_ENTITY)
    validation_set_indices += indices.tolist()

    return training_set_indices, validation_set_indices


def better_split_equal(data_entities):
    return better_split(data_entities, num_split=[20, 20, 4, 4])
