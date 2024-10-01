
from datetime import datetime
from dotenv import load_dotenv
import json
from openai import OpenAI
import os
from pathlib import Path
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select, DateTime
from sqlalchemy import update
from typing import Optional, Callable
from uuid import uuid4
from . import db, prompt
from .types import QueryCategory, PARAM_OVERRIDE_CACHE
from .utils import dict_hash, dict_equal
from ppa_commons import DataType, json_parse, heuristic_extract_entities

load_dotenv()

_CACHE_DIR = Path(os.getenv("LLM_QUERY_CACHE_DIR")) if os.getenv("LLM_QUERY_CACHE_DIR") else None

client = OpenAI()


QUERY_CATEGORY_TO_DATA_TYPE = {
    QueryCategory.DATA_ENTITY: DataType.ENTITY,
    QueryCategory.DATA_CLASSIFICATION: DataType.ENTITY,
    QueryCategory.PURPOSE_ENTITY: DataType.ENTITY,
    QueryCategory.PURPOSE_CLASSIFICATION: DataType.ENTITY,
    QueryCategory.PARTY_RECOGNITION: DataType.PARTY,
    QueryCategory.DATA_PRACTICE: DataType.ACTION,
    QueryCategory.RELATION_RECOGNITION: DataType.RELATION,
}


def parse(model_output_text: str, data_type: DataType = None) -> dict:
    text, obj = json_parse.try_parse_json_object(model_output_text)
    if data_type is not None:
        obj = heuristic_extract_entities(obj, data_type)
    return obj


def retrieve_entity_from_ambiguious_data(data: str|dict) -> str:
    entity_text = None
    if isinstance(data, str):
        entity_text = data
    elif isinstance(data, dict):
        entity_text = data['text']
    else:
        raise ValueError(f"Unexpected entity type: {type(data)}")
    return entity_text


class SQLiteCacheManager:
    '''
    A cache manager that uses SQLite to store cache.
    '''
    def __init__(self, cache_category: QueryCategory, llm_model: str):
        self.cache_category = cache_category
        self.llm_model = llm_model

    def get_from_cache(self, query_params: dict):
        with Session(db.engine) as session:
            hash_key = dict_hash(query_params)
            statement = select(db.QueryRecord).where(db.QueryRecord.hash_key == hash_key)
            for record in session.exec(statement):
                if dict_equal(record.query_params_dict(), query_params):
                    return record.lm_response, record
        return None

    def save_to_cache(self, query_params: dict, result: dict):
        with Session(db.engine) as session:
            record = db.QueryRecord(**{
                'query_params': query_params,
                'lm_response': result
            })
            session.add(record)
            session.commit()

    def update_cache(self, record: db.QueryRecord, result: dict):
        with Session(db.engine) as session:
            record.lm_response = result
            record.timestamp = datetime.now().isoformat()
            session.add(record)
            session.commit()


class QueryHelper(BaseModel):
    '''
    Helper class for running queries on LLM models.

    Cache is stored in the following directory structure:
    - LLM_QUERY_CACHE_DIR (from environment variable; no cache if not set)
        - cache_category (e.g., data_entity, purpose_entity, etc.; specified in the constructor)
            - llm_model
                - query_hash (generated from query parameters, which should be unique for each query)
                    - cache files (JSON files containing the query parameters and the result; multiple files may exist if hash collision occurs)
    '''
    cache_category: QueryCategory
    system_message: str
    user_message_template: str
    llm_model: str
    user_message_fn: Optional[Callable] = None

    _parse_ambiguous_data: bool = False

    def __init__(self, **data):
        super().__init__(**data)
        self._cache_manager = SQLiteCacheManager(cache_category=self.cache_category, llm_model=self.llm_model)

    def _execute_query(self, query_params: dict):
        completion = client.chat.completions.create(**query_params)
        model_output = completion.choices[0].message
        model_output_text = model_output.content
        return model_output_text

    def run_query(self, data: dict, override_cache: PARAM_OVERRIDE_CACHE = None):
        '''
        Run query, and return the parsed result (usually either a list or a dict).
        If anything wrong happens (e.g., API error, parsing error), throw an exception.

        For consistency, the passed `data` dictionary should always contain the following keys:
        - segment: str (the text segment to be analyzed)
        '''
        if self.user_message_fn:
            data.update(self.user_message_fn(data))
        user_message = self.user_message_template.format(**data)
        query_params = {
            "model": self.llm_model,
            "temperature": 0.0,
            "seed": 10000,
            "max_tokens": 1000,
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message}
            ]
        }
        cache_out = self._cache_manager.get_from_cache(query_params)
        if cache_out is not None:
            model_output_text, record = cache_out
            if override_cache:
                if override_cache is True or self.cache_category in override_cache:
                    model_output_text = self._execute_query(query_params)
                    self._cache_manager.update_cache(record, model_output_text)
        else:
            model_output_text = self._execute_query(query_params)
            self._cache_manager.save_to_cache(query_params, model_output_text)
        parsed_result = parse(model_output_text, QUERY_CATEGORY_TO_DATA_TYPE[self.cache_category])
        if self._parse_ambiguous_data:
            parsed_result = retrieve_entity_from_ambiguious_data(parsed_result)
        return parsed_result


Q_DATA_ENTITY = QueryHelper(
    cache_category=QueryCategory.DATA_ENTITY,
    system_message=prompt.SYSTEM_MESSAGE_DATA_ENTITY,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_DATA_ENTITY,
    llm_model="ft:gpt-4o-2024-08-06:rui:data-entity-sent-data-v3-d3:ACaCHoYc",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
    },
    _parse_ambiguous_data=True,
)

Q_DATA_CLASSIFICATION = QueryHelper(
    cache_category=QueryCategory.DATA_CLASSIFICATION,
    system_message=prompt.SYSTEM_MESSAGE_DATA_ENTITY_CLASSIFICATION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION,
    llm_model="ft:gpt-4o-2024-08-06:rui:data-class-sent-data-v2:A9HochjC",
)

Q_PURPOSE_ENTITY = QueryHelper(
    cache_category=QueryCategory.PURPOSE_ENTITY,
    system_message=prompt.SYSTEM_MESSAGE_PURPOSE_ENTITY,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_PURPOSE_ENTITY,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:purpose-span-sent-entity-v2:A97HPDpd",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
    },
    _parse_ambiguous_data=True,
)

Q_PURPOSE_CLASSIFICATION = QueryHelper(
    cache_category=QueryCategory.PURPOSE_CLASSIFICATION,
    system_message=prompt.SYSTEM_MESSAGE_PURPOSE_CATEGORY_CLASSIFICATION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_PURPOSE_CATEGORY,
    llm_model="ft:gpt-4o-2024-08-06:rui:purpose-class-sent-purpose-v2:A9KGkDmD",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
    },
)

Q_ACTION_RECOGNITION = QueryHelper(
    cache_category=QueryCategory.DATA_PRACTICE,
    system_message=prompt.SYSTEM_MESSAGE_ACTION_RECOGNITION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_ACTION_RECOGNITION,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:action-sent-v2:A9KKKeHG",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
        "segment": data["segment"],
    },
)

Q_PARTY_RECOGNITION = QueryHelper(
    cache_category=QueryCategory.PARTY_RECOGNITION,
    system_message=prompt.SYSTEM_MESSAGE_PARTY_RECOGNITION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_PARTY_RECOGNITION,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:party-sent-v3-d3:AAOzdio9",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
    },
)

Q_RELATION_RECOGNITION = QueryHelper(
    cache_category=QueryCategory.RELATION_RECOGNITION,
    system_message=prompt.SYSTEM_MESSAGE_RELATION_RECOGNITION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_RELATION_RECOGNITION,
    llm_model="ft:gpt-4o-2024-08-06:rui:relation-seg-v2:AAmgfsI1",
)
