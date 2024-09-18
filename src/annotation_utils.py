from pybrat.parser import BratParser, Entity, Event, Example, Relation
from .env import (
    BRAT_DATA_PATH,
    F_DATA_CATEGORY_DEFINITION,
    get_data_category_definitions,
)


def get_data_entity_types(data_def_file=F_DATA_CATEGORY_DEFINITION):
    return [k for k in get_data_category_definitions(data_def_file).keys()]


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
    brat = BratParser(error="ignore")
    annotations = brat.parse(brat_data_path)
    data_entities = get_data_entities_of_segments(annotations, data_def_file)
    return data_entities


def load_data_entities_of_sentences(brat_data_path=BRAT_DATA_PATH, data_def_file=F_DATA_CATEGORY_DEFINITION):
    brat = BratParser(error="ignore")
    annotations = brat.parse(brat_data_path)
    data_entities = get_data_entities_of_sentences(annotations, data_def_file)
    return data_entities
