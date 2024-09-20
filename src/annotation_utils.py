from enum import Enum
from functools import partial
from pybrat.parser import BratParser, Entity, Event, Example, Relation
from .env import (
    BRAT_DATA_PATH,
    F_DATA_CATEGORY_DEFINITION,
    F_PURPOSE_CATEGORY_DEFINITION,
    PROTECTION_METHODS,
    PARTY_ENTITIES,
    get_entity_category_definitions,
)


class ActionType(Enum):
    COLLECTION_USE = "collection-use"
    FIRST_PARTY_COLLECTION_USE = "first-party-collection-use"
    THIRD_PARTY_COLLECTION_USE = "third-party-collection-use"
    THIRD_PARTY_SHARING_DISCLOSURE = "third-party-sharing-disclosure"
    STORAGE_RETENTION_DELETION = "data-storage-retention-deletion"
    SECURITY_PROTECTION = "data-security-protection"


def get_data_entity_types(data_def_file=F_DATA_CATEGORY_DEFINITION):
    return [k for k in get_entity_category_definitions(data_def_file).keys()]


def get_purpose_entity_types(purpose_def_file=F_PURPOSE_CATEGORY_DEFINITION):
    return [k for k in get_entity_category_definitions(purpose_def_file).keys()]


def load_and_get(get_fn, brat_data_path=BRAT_DATA_PATH):
    brat = BratParser(error="ignore")
    annotations = brat.parse(brat_data_path)
    annotations = with_correct_use_type(annotations)
    return get_fn(annotations)


def get_segment_type_entities(annotations, types):
    '''
    Get all text spans that are entities (of the specified types) in the same segment, and put them together.
    For example, the types can be data types, and this function gets all data entities, organised by segments.
    Output structure is:
    [
        {
            "segment": segment_text,
            "entities": [
                {
                    "text": text_span,
                    "type": type
                }
            ]
        }
    ]
    where the same segment is always grouped together.
    '''
    res = {}
    for x in annotations:
        if x.text not in res:
            res[x.text] = []
        part = res[x.text]
        for e in x.entities:
            if e.type in types:
                part.append({
                    "text": e.mention,
                    "type": e.type
                })
    return [{"segment": k, "entities": v} for k, v in res.items()]


def get_sentence_type_entities(annotations, types):
    '''
    Get all text spans that are entities (of the specified types) in the same sentence, and put them together.
    For example, the types can be data types, and this function gets all data entities, organised by sentences, then segments.
    Output structure is:
    [
        {
            "segment": segment_text,
            "sentence": sentence_text,
            "entities": [
                {
                    "text": text_span,
                    "type": type
                }
            ]
        }
    ]
    where the same segment is always grouped together.
    '''
    def is_within_sentence(span, sentence_span):
        return span.start >= sentence_span[0] and span.end <= sentence_span[1]

    res = {}
    for x in annotations:
        segment = x.text
        sentences = segment.split('\n')
        #sentence_spans is a list of tuples, each tuple is the start and end index of a sentence
        sentence_spans = [(segment.index(s), segment.index(s) + len(s)) for s in sentences]
        sentences = [s.strip() for s in sentences]
        for sentence in sentences:
            if (segment, sentence) not in res:
                res[(segment, sentence)] = []
        for i, sentence_span in enumerate(sentence_spans):
            part = res[(segment, sentences[i])]
            for e in x.entities:
                if e.type in types:
                    for span in e.spans:
                        if is_within_sentence(span, sentence_span):
                            part.append({
                                "text": e.mention,
                                "type": e.type,
                            })
    return [{"segment": seg, "sentence": sent, "entities": v} for (seg, sent), v in res.items()]


def get_data_entities_of_segments(annotations, data_def_file=F_DATA_CATEGORY_DEFINITION):
    data_types = list(get_data_entity_types(data_def_file))

    data_entities = get_segment_type_entities(annotations, data_types)

    return data_entities


def get_data_entities_of_sentences(annotations, data_def_file=F_DATA_CATEGORY_DEFINITION):
    data_types = list(get_data_entity_types(data_def_file))

    data_entities = get_sentence_type_entities(annotations, data_types)

    return data_entities


def load_data_entities_of_segments(brat_data_path=BRAT_DATA_PATH, data_def_file=F_DATA_CATEGORY_DEFINITION):
    return load_and_get(partial(get_data_entities_of_segments, data_def_file=data_def_file), brat_data_path)


def load_data_entities_of_sentences(brat_data_path=BRAT_DATA_PATH, data_def_file=F_DATA_CATEGORY_DEFINITION):
    return load_and_get(partial(get_data_entities_of_sentences, data_def_file=data_def_file), brat_data_path)


def get_purpose_entities_of_segments(annotations, purpose_def_file=F_PURPOSE_CATEGORY_DEFINITION):
    purpose_types = list(get_purpose_entity_types(purpose_def_file))

    purpose_entities = get_segment_type_entities(annotations, purpose_types)

    return purpose_entities


def get_purpose_entities_of_sentences(annotations, purpose_def_file=F_PURPOSE_CATEGORY_DEFINITION):
    purpose_types = list(get_purpose_entity_types(purpose_def_file))

    purpose_entities = get_sentence_type_entities(annotations, purpose_types)

    return purpose_entities


def load_purpose_entities_of_segments(brat_data_path=BRAT_DATA_PATH, purpose_def_file=F_PURPOSE_CATEGORY_DEFINITION):
    return load_and_get(partial(get_purpose_entities_of_segments, purpose_def_file=purpose_def_file), brat_data_path)


def load_purpose_entities_of_sentences(brat_data_path=BRAT_DATA_PATH, purpose_def_file=F_PURPOSE_CATEGORY_DEFINITION):
    return load_and_get(partial(get_purpose_entities_of_sentences, purpose_def_file=purpose_def_file), brat_data_path)


C_DATA_COLLECTOR = "Data-Collector"
C_FIRST_PARTY_ENTITY = "First-party-entity"
C_THIRD_PARTY_ENTITY = "Third-party-entity"


def with_correct_use_type(annotations):
    '''
    Changes in-place
    '''
    for x in annotations:
        for e in x.events:
            if e.type == ActionType.COLLECTION_USE.value:
                for arg in e.arguments:
                    if arg.role == C_DATA_COLLECTOR:
                        if arg.object.type == C_FIRST_PARTY_ENTITY:
                            e.type = ActionType.FIRST_PARTY_COLLECTION_USE.value
                            break
                        elif arg.object.type == C_THIRD_PARTY_ENTITY:
                            e.type = ActionType.THIRD_PARTY_COLLECTION_USE.value
                            break
    return annotations


def is_within_sentence(span, sentence_span):
    return span.start >= sentence_span[0] and span.end <= sentence_span[1]


def get_sentences_with_spans(annotation):
    segment = annotation.text
    sentences = segment.split('\n')
    #sentence_spans is a list of tuples, each tuple is the start and end index of a sentence
    sentence_spans = [(segment.index(s), segment.index(s) + len(s)) for s in sentences]
    sentences = [s.strip() for s in sentences]
    return dict(zip(sentence_spans, sentences))


def get_actions_of_segments(annotations):
    '''
    Get all text spans and sentences that are actions.
    Output structure is:
    [
        {
            "segment": SEGMENT,
            "entities": [
                {
                    "sentence": SENTENCE,
                    "action_type": ACTION_TYPE,
                    "text": TEXT_OF_THE_ACTION
                }
            ]
        }
    ]

    where the same segment is always grouped together.
    '''
    res = []
    for x in annotations:
        segment_text = x.text
        sentences = get_sentences_with_spans(x)

        parts = []

        for e in x.events:
            type = e.type
            text = e.trigger.mention
            span = e.trigger.spans[0]
            for span2 in sentences.keys():
                if is_within_sentence(span, span2):
                    sentence = sentences[span2]
                    break
            assert sentence
            parts.append({
                "action_type": type,
                "text": text,
                "sentence": sentence,
            })

        res.append({
            "segment": segment_text,
            "entities": parts,
        })

    return res


def get_actions_of_sentences(annotations):
    '''
    Get all text spans and sentences that are actions, for each sentence.
    Output structure is:
    [
        {
            "segment": SEGMENT,
            "sentence": SENTENCE,
            "entities": [
                {
                    "action_type": ACTION_TYPE,
                    "text": TEXT_OF_THE_ACTION
                }
            ]
        }
    ]

    where the same segment and sentence is always grouped together.
    '''
    res = {}
    for x in annotations:
        segment_text = x.text
        sentences = get_sentences_with_spans(x)

        for span, sentence in sentences.items():
            res[(segment_text, sentence)] = []

        for e in x.events:
            type = e.type
            text = e.trigger.mention
            span = e.trigger.spans[0]
            for span2 in sentences.keys():
                if is_within_sentence(span, span2):
                    sentence = sentences[span2]
                    break
            assert sentence
            parts = res[(segment_text, sentence)]
            parts.append({
                "action_type": type,
                "text": text,
            })

    return [{"segment": seg, "sentence": sent, "entities": v} for (seg, sent), v in res.items()]


def load_actions_of_segments(brat_data_path=BRAT_DATA_PATH):
    return load_and_get(get_actions_of_segments, brat_data_path)


def get_protection_methods_of_segments(annotations):
    return get_segment_type_entities(annotations, PROTECTION_METHODS)


def get_protection_methods_of_sentences(annotations):
    return get_sentence_type_entities(annotations, PROTECTION_METHODS)


def get_party_entities_of_segments(annotations):
    return get_segment_type_entities(annotations, PARTY_ENTITIES)


def get_party_entities_of_sentences(annotations):
    return get_sentence_type_entities(annotations, PARTY_ENTITIES)
