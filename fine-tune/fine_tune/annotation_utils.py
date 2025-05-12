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


def is_within_sentence(span, sentence_span):
    return span.start >= sentence_span[0] and span.end <= sentence_span[1]


def get_sentences_with_spans(annotation):
    segment = annotation.text
    sentences = segment.split('\n')
    sentences = [s for s in [s.strip() for s in sentences] if s]
    #sentence_spans is a list of tuples, each tuple is the start and end index of a sentence
    sentence_spans = [(segment.index(s), segment.index(s) + len(s)) for s in sentences]
    sentences = [s.strip() for s in sentences]
    return dict(zip(sentence_spans, sentences))


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

    res = {}
    for x in annotations:
        segment = x.text
        sentences = get_sentences_with_spans(x)

        for sentence in sentences.values():
            if (segment, sentence) not in res:
                res[(segment, sentence)] = []
        for sentence_span, sentence in sentences.items():
            part = res[(segment, sentence)]
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


def get_data_entities_with_actions_of_segments(annotations, data_def_file=F_DATA_CATEGORY_DEFINITION):
    data_types = list(get_data_entity_types(data_def_file))

    res = {}
    for x in annotations:
        segment_text = x.text
        res[segment_text] = []
        parts = res[segment_text]
        for e in x.events:
            for arg in e.arguments:
                if arg.object.type in data_types:
                    parts.append({
                        "action_context": e.type,
                        "text": arg.object.mention,
                        "type": arg.object.type
                    })
    return [{"segment": k, "entities": v} for k, v in res.items()]


def get_data_entities_with_actions_of_sentences(annotations, data_def_file=F_DATA_CATEGORY_DEFINITION):
    data_types = list(get_data_entity_types(data_def_file))

    data_entities = get_segment_type_entities(annotations, data_types)

    res = {}
    for x in annotations:
        segment = x.text
        sentences = get_sentences_with_spans(x)

        for sentence in sentences.values():
            if (segment, sentence) not in res:
                res[(segment, sentence)] = []
        for sentence_span, sentence in sentences.items():
            part = res[(segment, sentence)]
            for e in x.events:
                for arg in e.arguments:
                    e1 = arg.object
                    if e1.type in data_types:
                        for span in e1.spans:
                            if is_within_sentence(span, sentence_span):
                                part.append({
                                    "action_context": e.type,
                                    "text": e1.mention,
                                    "type": e1.type,
                                })
    return [{"segment": seg, "sentence": sent, "entities": v} for (seg, sent), v in res.items()]


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


def get_party_entities_of_segments_v2(annotations):
    '''
    On top of the output of get_party_entities_of_segments, this function will:
    Also merge Third-party-name into Third-party-entity.
    '''
    res = get_segment_type_entities(annotations, PARTY_ENTITIES)
    for x in res:
        for y in x['entities']:
            if y['type'] == 'Third-party-name':
                y['type'] = 'Third-party-entity'
    return res


def get_party_entities_of_sentences_v2(annotations):
    '''
    On top of the output of get_party_entities_of_sentences, this function will:
    Also merge Third-party-name into Third-party-entity.
    '''
    res = get_sentence_type_entities(annotations, PARTY_ENTITIES)
    for x in res:
        for y in x['entities']:
            if y['type'] == 'Third-party-name':
                y['type'] = 'Third-party-entity'
    return res


def get_relations_of_segment_sentences_no_subsume(annotations):
    '''
    Get all relations of each action in sentences in the same segment, paired together.
    Output has the structure:
    [
        {
            "segment": SEGMENT,
            "entities": [
                {
                    "sentence": SENTENCE,
                    "action_type": ACTION_TYPE,
                    "relations": [
                        {
                            "relation_type": RELATION_TYPE,
                            "entity": TEXT_OF_THE_RELATED_ENTITY,
                            "entity_type": ENTITY_TYPE
                        }
                    ]
                }
            ]
        }
    ]
    where the same action type of the same sentence is always grouped together.
    '''

    action_entities = get_actions_of_sentences(annotations)
    action_entities_dict = {(x["segment"], x["sentence"]): x["entities"] for x in action_entities}

    res = {}
    for x in annotations:
        segment_text = x.text
        sentences = get_sentences_with_spans(x)

        for span, sentence in sentences.items():
            res[segment_text] = {}

        for e in x.events:
            action_type = e.type
            span = e.trigger.spans[0]
            for span2 in sentences.keys():
                if is_within_sentence(span, span2):
                    sentence = sentences[span2]
                    break
            assert sentence
            sub_dict = res[segment_text]
            if (sentence, action_type) not in sub_dict:
                sub_dict[(sentence, action_type)] = []
            parts = sub_dict[(sentence, action_type)]
            for arg in e.arguments:
                role = arg.role
                entity = arg.object
                entity_type = entity.type
                entity_mention = entity.mention
                parts.append({
                    "relation_type": role,
                    "entity": entity_mention,
                    "entity_type": entity_type,
                })

    ret = []
    for segement_text, v in res.items():
        l2 = []
        for (sentence, action_type), relations in v.items():
            l2.append({
                "sentence": sentence,
                "action_type": action_type,
                "relations": relations,
            })
        l1 = {
            'segment': segement_text,
            'entities': l2,
        }
        ret.append(l1)
    return ret


def get_relations_of_segment_sentences_no_subsume_v2(annotations):
    '''
    Get all relations of each action in sentences in the same segment, paired together.
    On top of the output of get_relations_of_segment_sentences_no_subsume, this function will:
    Also replace the specific data and purpose entity types with general types (Data and Purpose).
    '''

    res = get_relations_of_segment_sentences_no_subsume(annotations)

    data_entity_types = get_data_entity_types()
    data_entity_types += ['Data-general', 'Data-other']
    data_entity_type_replace = 'Data'
    purpose_entity_types = get_purpose_entity_types()
    purpose_entity_types += ['Purpose-general', 'Purpose-other']
    purpose_entity_type_replace = 'Purpose'

    for x in res:
        for y in x['entities']:
            for z in y['relations']:
                if z['entity_type'] in data_entity_types:
                    z['entity_type'] = data_entity_type_replace
                elif z['entity_type'] in purpose_entity_types:
                    z['entity_type'] = purpose_entity_type_replace

    return res


def get_relations_of_segment_sentences_no_subsume_v3(annotations):
    '''
    Get all relations of each action in sentences in the same segment, paired together.
    On top of the output of get_relations_of_segment_sentences_no_subsume, this function will:
    Also replace the specific data and purpose entity types with general types (Data and Purpose).
    Also merge Third-party-name into Third-party-entity.
    '''

    res = get_relations_of_segment_sentences_no_subsume(annotations)

    data_entity_types = get_data_entity_types()
    data_entity_types += ['Data-general', 'Data-other']
    data_entity_type_replace = 'Data'
    purpose_entity_types = get_purpose_entity_types()
    purpose_entity_types += ['Purpose-general', 'Purpose-other']
    purpose_entity_type_replace = 'Purpose'
    party_entity_override = {
        'Third-party-name': 'Third-party-entity',
    }

    for x in res:
        for y in x['entities']:
            for z in y['relations']:
                if z['entity_type'] in data_entity_types:
                    z['entity_type'] = data_entity_type_replace
                elif z['entity_type'] in purpose_entity_types:
                    z['entity_type'] = purpose_entity_type_replace
                elif z['entity_type'] in party_entity_override:
                    z['entity_type'] = party_entity_override[z['entity_type']]

    return res


def get_relations_of_sentences_no_subsume(annotations):
    '''
    (Derived from `get_relations_of_segment_sentences_no_subsume`)
    Get all relations of each action in sentences.
    Output has the structure:
    [
        {
            "segment": SEGMENT,
            "sentence": SENTENCE,
            "entities": [
                {
                    "action_type": ACTION_TYPE,
                    "relations": [
                        {
                            "relation_type": RELATION_TYPE,
                            "entity": TEXT_OF_THE_RELATED_ENTITY,
                            "entity_type": ENTITY_TYPE
                        }
                    ]
                }
            ]
        }
    ]
    where the same action type of the same sentence is always grouped together.

    Note: This function currently doesn't handle cross-sentence relations.
    '''

    action_entities = get_actions_of_sentences(annotations)
    action_entities_dict = {(x["segment"], x["sentence"]): x["entities"] for x in action_entities}

    res = {}
    for x in annotations:
        segment_text = x.text
        sentences = get_sentences_with_spans(x)

        for span, sentence in sentences.items():
            if (segment_text, sentence) not in res:  # This should always be true. But better check first.
                res[(segment_text, sentence)] = {}

        for e in x.events:
            action_type = e.type
            span = e.trigger.spans[0]
            for span2 in sentences.keys():
                if is_within_sentence(span, span2):
                    sentence = sentences[span2]
                    break
            assert sentence
            sub_dict = res[(segment_text, sentence)]
            if action_type not in sub_dict:
                sub_dict[action_type] = []
            parts = sub_dict[action_type]
            for arg in e.arguments:
                role = arg.role
                entity = arg.object
                entity_type = entity.type
                entity_mention = entity.mention
                parts.append({
                    "relation_type": role,
                    "entity": entity_mention,
                    "entity_type": entity_type,
                })

    ret = []
    for (segement_text, sentence), v in res.items():
        l2 = []
        for action_type, relations in v.items():
            l2.append({
                "action_type": action_type,
                "relations": relations,
            })
        l1 = {
            'segment': segement_text,
            'sentence': sentence,
            'entities': l2,
        }
        ret.append(l1)
    return ret


def get_subsume_relations_of_segment_sentences(annotations):
    '''
    Get all relations of type "SUBSUME" of each action in sentences in the same segment, paired together.
    Output has this structure:
    [
        {
            "segment": SEGMENT,
            "entities": [
                {
                    "sentence": SENTENCE,
                    "relations": [
                        {
                            "subsumed": (TEXT_OF_THE_SUBSUMED_ENTITY, span),
                            "subsuming": (TEXT_OF_THE_SUBSUMING_ENTITY, span),
                        }
                    ]
                }
            ]
        }
    ]
    where the same action type of the same sentence is always grouped together.
    '''
    res = {}
    for x in annotations:
        segment_text = x.text
        sentences = get_sentences_with_spans(x)

        res[segment_text] = {}
        sub_dict = res[segment_text]

        for span, sentence in sentences.items():
            res[segment_text][sentence] = []

        for r in x.relations:
            relation_type = r.type
            if relation_type == 'SUBSUME':
                arg1 = (r.arg1.mention, r.arg1.spans[0])
                arg2 = (r.arg2.mention, r.arg2.spans[0])
                span = r.arg1.spans[0]
                for span2 in sentences.keys():
                    if is_within_sentence(span, span2):
                        sentence = sentences[span2]
                        break
                assert sentence
                assert sentence in sub_dict
                parts = sub_dict[sentence]
                parts.append({
                    "subsumed": arg1,
                    "subsuming": arg2,
                })

    ret = []
    for segement_text, v in res.items():
        l2 = []
        for sentence, relations in v.items():
            l2.append({
                "sentence": sentence,
                "relations": relations,
            })
        l1 = {
            'segment': segement_text,
            'entities': l2,
        }
        ret.append(l1)
    return ret


def get_subsume_relations_of_sentences(annotations):
    '''
    Get all relations of type "SUBSUME" of each action in sentences.
    Output has this structure:
    [
        {
            "sentence": SENTENCE,
            "entities": [
                {
                    "subsumed": (TEXT_OF_THE_SUBSUMED_ENTITY, span),
                    "subsuming": (TEXT_OF_THE_SUBSUMING_ENTITY, span),
                }
            ]
        }
    ]
    '''
    subsume_relations_of_segment_sentences = get_subsume_relations_of_segment_sentences(annotations)
    res = []
    for segment in subsume_relations_of_segment_sentences:
        for x in segment['entities']:
            res.append({
                "sentence": x['sentence'],
                "entities": x['relations'],
            })
    return res


def get_retention_details_of_sentences(annotations):
    '''
    Get details of the `data-storage-retention-deletion` actions in sentences.
    Output has the structure:
    [
        {
            "segment": SEGMENT,
            "sentence": SENTENCE,
            "items": [
                {
                    "storage-place": STORAGE_PLACE,
                    "retention-period": RETENTION_PERIOD
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
            if e.type == ActionType.STORAGE_RETENTION_DELETION.value:
                dic = {
                    'text': e.trigger.mention,
                }
                for arg in e.arguments:
                    obj = arg.object
                    if obj.type == 'storage-place':
                        dic["storage-place"] = obj.mention
                    elif obj.type == 'retention-period':
                        dic["retention-period"] = obj.mention
                span = e.trigger.spans[0]
                for span2 in sentences.keys():
                    if is_within_sentence(span, span2):
                        sentence = sentences[span2]
                        break
                assert sentence
                parts = res[(segment_text, sentence)]
                parts.append(dic)

    return [{"segment": seg, "sentence": sent, "items": v} for (seg, sent), v in res.items()]

