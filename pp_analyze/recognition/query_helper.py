from datetime import datetime
from deepdiff import DeepDiff, DeepHash
from dotenv import load_dotenv
import json
from openai import OpenAI
import os
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Callable
from uuid import uuid4
from . import prompt
from pp_analyze.external import json_parse


load_dotenv()

_CACHE_DIR = Path(os.getenv("LLM_QUERY_CACHE_DIR")) if os.getenv("LLM_QUERY_CACHE_DIR") else None

client = OpenAI()


def parse(model_output_text: str):
    text, obj = json_parse.try_parse_json_object(model_output_text)
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


def _dict_equal(d1, d2):
    diff = DeepDiff(d1, d2)
    return not diff


class CacheManager:

    def __init__(self, cache_category: str, llm_model: str):
        self.cache_category = cache_category
        self.llm_model = llm_model

    def _cache_dir(self, query_params: dict, auto_create: bool = True):
        query_hash = DeepHash(query_params)[query_params]
        cache_dir: Path = _CACHE_DIR / self.cache_category / self.llm_model / query_hash
        if not cache_dir.exists() and auto_create:
            cache_dir.mkdir(parents=True)
        return cache_dir

    def get_from_cache(self, query_params: dict):
        if _CACHE_DIR is None:
            return None
        cache_dir = self._cache_dir(query_params)
        for file in cache_dir.iterdir():
            if file.is_file() and file.suffix == '.json':
                with file.open("r") as f:
                    cached_obj = json.load(f)
                    if _dict_equal(cached_obj['query_params'], query_params):
                        return cached_obj['result']
        return None

    def save_to_cache(self, query_params: dict, result: dict):
        if _CACHE_DIR is None:
            return
        cache_dir = self._cache_dir(query_params)
        filename = f"{uuid4()}.json"
        cache_file = cache_dir / filename
        with cache_file.open("w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "query_params": query_params,
                "result": result
            }, f)



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
    cache_category: str
    system_message: str
    user_message_template: str
    llm_model: str
    user_message_fn: Optional[Callable] = None

    _parse_ambiguous_data: bool = False

    def __init__(self, **data):
        super().__init__(**data)
        self._cache_manager = CacheManager(cache_category=self.cache_category, llm_model=self.llm_model)

    def run_query(self, data: dict):
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
            "temperature": 0,
            "seed": 10000,
            "max_tokens": 1000,
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message}
            ]
        }
        model_output_text = self._cache_manager.get_from_cache(query_params)
        if model_output_text is None:
            completion = client.chat.completions.create(**query_params)
            model_output = completion.choices[0].message
            model_output_text = model_output.content
            self._cache_manager.save_to_cache(query_params, model_output_text)
        parsed_result = parse(model_output_text)
        if self._parse_ambiguous_data:
            parsed_result = retrieve_entity_from_ambiguious_data(parsed_result)
        return parsed_result


Q_DATA_ENTITY = QueryHelper(
    cache_category="data_entity",
    system_message=prompt.SYSTEM_MESSAGE_DATA_ENTITY,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_DATA_ENTITY,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:data-entity-sent-data-ver2:A8ycyw3W",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
        "segment": data["segment"],
    },
    _parse_ambiguous_data=True,
)

Q_DATA_CLASSIFICATION = QueryHelper(
    cache_category="data_classification",
    system_message=prompt.SYSTEM_MESSAGE_DATA_ENTITY_CLASSIFICATION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION,
    llm_model="ft:gpt-4o-2024-08-06:rui:data-class-sent-data-v2:A9HochjC",
)

Q_PURPOSE_ENTITY = QueryHelper(
    cache_category="purpose_entity",
    system_message=prompt.SYSTEM_MESSAGE_PURPOSE_ENTITY,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_PURPOSE_ENTITY,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:purpose-span-sent-entity-v2:A97HPDpd",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
    },
    _parse_ambiguous_data=True,
)

Q_PURPOSE_CLASSIFICATION = QueryHelper(
    cache_category="purpose_classification",
    system_message=prompt.SYSTEM_MESSAGE_PURPOSE_CATEGORY_CLASSIFICATION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_PURPOSE_CATEGORY,
    llm_model="ft:gpt-4o-2024-08-06:rui:purpose-class-sent-purpose-v2:A9KGkDmD",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
    },
)

Q_ACTION_RECOGNITION = QueryHelper(
    cache_category="action_recognition",
    system_message=prompt.SYSTEM_MESSAGE_ACTION_RECOGNITION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_ACTION_RECOGNITION,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:action-sent-v2:A9KKKeHG",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
        "segment": data["segment"],
    },
)

Q_PARTY_RECOGNITION = QueryHelper(
    cache_category="party_recognition",
    system_message=prompt.SYSTEM_MESSAGE_PARTY_RECOGNITION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_PARTY_RECOGNITION,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:party-sent-v3-d3:AAOzdio9",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
    },
)

Q_RELATION_RECOGNITION = QueryHelper(
    cache_category="relation_recognition",
    system_message=prompt.SYSTEM_MESSAGE_RELATION_RECOGNITION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_RELATION_RECOGNITION,
    llm_model="ft:gpt-4o-2024-08-06:rui:relation-seg-v2:AAmgfsI1",
)
