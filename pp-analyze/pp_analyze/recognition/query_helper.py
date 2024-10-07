import asyncio
from datetime import datetime
from dotenv import load_dotenv
import json
import logging
from openai import OpenAI
import os
from pathlib import Path
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select, DateTime
from sqlalchemy import update
import tempfile
from tqdm.auto import tqdm
from typing import Optional, Callable
from uuid import uuid4
from . import db, prompt
from .types import QueryCategory, PARAM_OVERRIDE_CACHE
from .utils import dict_hash, dict_equal
from ppa_commons import DataType, json_parse, heuristic_extract_entities

load_dotenv()

_CACHE_DIR = Path(os.getenv("LLM_QUERY_CACHE_DIR")) if os.getenv("LLM_QUERY_CACHE_DIR") else None

client = OpenAI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


WAIT_INTERVAL = 30


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


class SQLiteCacheManager:
    '''
    A cache manager that uses SQLite to store cache.
    '''
    def __init__(self, cache_category: QueryCategory, llm_model: str):
        self.cache_category = cache_category
        self.llm_model = llm_model

    def get_record_from_cache(self, query_params: dict):
        with Session(db.engine) as session:
            hash_key = dict_hash(query_params)
            statement = select(db.QueryRecord).where(db.QueryRecord.hash_key == hash_key)
            for record in session.exec(statement):
                if dict_equal(record.query_params_dict(), query_params):
                    return record.lm_response, record
        return None

    def get_batch_record_from_cache(self, query_params: Optional[dict] = None):
        with Session(db.engine) as session:
            statement = select(db.BatchQueryRecord)
            hash_key = dict_hash(query_params)
            statement = statement.where(db.BatchQueryRecord.hash_key == hash_key)
            for record in session.exec(statement):
                if query_params and dict_equal(record.query_params_dict(), query_params):
                    return record
        return None

    def find_batch_records_from_cache(self, batch_id: str):
        with Session(db.engine) as session:
            statement = select(db.BatchQueryRecord)
            if batch_id:
                statement = statement.where(db.BatchQueryRecord.batch_id == batch_id)
            res: list[db.BatchQueryRecord] = []
            for record in session.exec(statement):
                res.append(record)
        return res

    def save_to_cache(self, query_params: dict, result: dict):
        with Session(db.engine) as session:
            record = db.QueryRecord(**{
                'query_params': query_params,
                'lm_response': result
            })
            session.add(record)
            session.commit()

    def save_batch_job_to_cache(self, query_params: dict, batch_job_id: str, batch_custom_id: str):
        with Session(db.engine) as session:
            record = db.BatchQueryRecord(**{
                'query_params': query_params,
                'batch_id': batch_job_id,
                'batch_custom_id': batch_custom_id
            })
            session.add(record)
            session.commit()

    def update_cache(self, record: db.QueryRecord, result: str):
        with Session(db.engine) as session:
            record.lm_response = result
            record.timestamp = datetime.now().isoformat()
            session.add(record)
            session.commit()

    def fill_batch_job_cache(self, batch_record: db.BatchQueryRecord, result: str):
        '''
        Convert the batch job record to a query record, and fill the lm_response field with result. Remove the batch job record.
        '''
        with Session(db.engine) as session:
            query_record = db.QueryRecord(**{
                'query_params': batch_record.query_params,
                'lm_response': result
            })
            session.add(query_record)
            session.delete(batch_record)
            session.commit()


def to_jsonl(data_set):
    content = ''
    for data in data_set:
        p = json.dumps(data)
        content += p + '\n'
    return content


def from_jsonl(jsonl_str):
    return [json.loads(line) for line in jsonl_str.split('\n') if line]


async def wait_for_batch_job_finish(batch_job_id):
    while True:
        job = client.batches.retrieve(batch_job_id)
        if job.status not in {'validating', 'in_progress', 'finalizing', 'cancelling'}:
            break
        await asyncio.sleep(WAIT_INTERVAL)
    return job


async def retrieve_batch_job_results(batch_job):
    if isinstance(batch_job, str):
        batch_job = await wait_for_batch_job_finish(batch_job)
    else:
        batch_job = await wait_for_batch_job_finish(batch_job.id)
    output_file_id = batch_job.output_file_id
    file_response = client.files.content(output_file_id)
    return file_response.text


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
    parse_ambiguous_data: bool = False

    def __init__(self, **data):
        super().__init__(**data)
        self._cache_manager = SQLiteCacheManager(cache_category=self.cache_category, llm_model=self.llm_model)
        self._batch_query_queue = []
        self._batch_jobs = []

    def _get_query_params(self, data: dict):
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
        return query_params

    def _execute_query(self, query_params: dict):
        '''
        Execute the query and return the model output text.
        Not in batch mode.
        '''
        completion = client.chat.completions.create(**query_params)
        model_output = completion.choices[0].message
        model_output_text = model_output.content
        return model_output_text

    def enqueue_batch_query(self, data: dict, override_cache: PARAM_OVERRIDE_CACHE = None):
        query_params = self._get_query_params(data)
        cache_out = self._cache_manager.get_record_from_cache(query_params)
        if not cache_out:
            cache_out = self._cache_manager.get_batch_record_from_cache(query_params)
            if cache_out and cache_out.batch_id not in self._batch_jobs:
                self._batch_jobs.append(cache_out.batch_id)
                logger.info(f"Picked-up unprocessed previous batch job: {cache_out.batch_id}")
        if cache_out and (not override_cache or self.cache_category not in override_cache):
            return
        self._batch_query_queue.append(query_params)
        return len(self._batch_query_queue)

    def enqueue_batch_queries(self, data: list[dict], override_cache: PARAM_OVERRIDE_CACHE = None, execute_now: bool = False):
        for d in data:
            self.enqueue_batch_query(d, override_cache)
        if execute_now:
            return self.execute_batch_queries()

    def execute_batch_queries(self):
        if not self._batch_query_queue:
            return []
        batch_input_list = []
        for i, query_params in tqdm(enumerate(self._batch_query_queue), desc="Composing batch query file", leave=False):
            data_item = {
                'custom_id': f"request-{i}",
                'method': 'POST',
                'url': '/v1/chat/completions',
                'body': query_params
            }
            batch_input_list.append(data_item)
        fd, batch_input_file = tempfile.mkstemp('.jsonl', 'batch')
        with open(batch_input_file, 'w') as f:
            f.write(to_jsonl(batch_input_list))
            f.flush()
        batch_input_file_remote = client.files.create(
            file=open(batch_input_file, "rb"),
            purpose="batch"
        )
        batch_job = client.batches.create(
            input_file_id=batch_input_file_remote.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": f"Batch analyze for {self.cache_category}",
            }
        )
        self._batch_jobs.append(batch_job.id)
        batch_job_id = batch_job.id
        for i, query_params in tqdm(enumerate(self._batch_query_queue), desc="Saving batch job to cache", leave=False):
            self._cache_manager.save_batch_job_to_cache(query_params, batch_job_id, f"request-{i}")
        num_queries = len(self._batch_query_queue)
        self._batch_query_queue = []
        return batch_job.id, num_queries, self._batch_jobs

    async def wait_and_handle_batch_queries(self, batch_job_id=None):
        if batch_job_id is None:
            batch_jobs = [job for job in self._batch_jobs]
        else:
            batch_jobs = [batch_job_id]
        finished_jobs = []
        for i_batch_job_id in (pbar := tqdm(batch_jobs, desc="Waiting for batch jobs", leave=False)):
            pbar.set_postfix_str(f"Waiting for batch job {i_batch_job_id} finish")
            res = await retrieve_batch_job_results(i_batch_job_id)
            pbar.set_postfix_str('')
            records = self._cache_manager.find_batch_records_from_cache(batch_id=i_batch_job_id)
            assert isinstance(records, list)
            if not records:
                finished_jobs.append(i_batch_job_id)
                continue
            record_dict = {record.batch_custom_id: record for record in records}
            for data_item in tqdm(from_jsonl(res), desc="Handling results", leave=False):
                record = record_dict[data_item['custom_id']]
                self._cache_manager.fill_batch_job_cache(record, result=data_item['response']['body']['choices'][0]['message']['content'])
            finished_jobs.append(i_batch_job_id)
        self._batch_jobs = [job for job in self._batch_jobs if job not in finished_jobs]

    def run_query(self, data: dict, override_cache: PARAM_OVERRIDE_CACHE = None, batch: bool = False):
        '''
        Run query, and return the parsed result (usually either a list or a dict).
        If anything wrong happens (e.g., API error, parsing error), throw an exception.

        For consistency, the passed `data` dictionary should always contain the following keys:
        - segment: str (the text segment to be analyzed)
        '''
        query_params = self._get_query_params(data)
        cache_out = self._cache_manager.get_record_from_cache(query_params)
        if not cache_out and batch:
            raise RuntimeError("Batch job should be enqueued and executed using `enqueue_batch_queries` and `execute_batch_queries` before calling this function.")
        if cache_out is not None and (not override_cache or self.cache_category not in override_cache):
            model_output_text, _ = cache_out
        else:
            if not batch:
                model_output_text = self._execute_query(query_params)
                if cache_out:
                    _, record = cache_out
                    self._cache_manager.update_cache(record, model_output_text)
                else:
                    self._cache_manager.save_to_cache(query_params, model_output_text)
            else:
                raise RuntimeError("Batch job should be waited and handled by `wait_and_handle_batch_queries` before calling this function.")
        parsed_result = parse(model_output_text, QUERY_CATEGORY_TO_DATA_TYPE[self.cache_category] if self.parse_ambiguous_data else None)
        return parsed_result


Q_DATA_ENTITY = QueryHelper(
    cache_category=QueryCategory.DATA_ENTITY,
    system_message=prompt.SYSTEM_MESSAGE_DATA_ENTITY,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_DATA_ENTITY,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:data-entity-sent-data-v3-d4:ADJvRrJP",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
    },
    parse_ambiguous_data=True,
)

Q_DATA_CLASSIFICATION = QueryHelper(
    cache_category=QueryCategory.DATA_CLASSIFICATION,
    system_message=prompt.SYSTEM_MESSAGE_DATA_ENTITY_CLASSIFICATION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION,
    llm_model="ft:gpt-4o-2024-08-06:rui:data-class-sent-data-v2-d4:AEkSuIYg",
)

Q_PURPOSE_ENTITY = QueryHelper(
    cache_category=QueryCategory.PURPOSE_ENTITY,
    system_message=prompt.SYSTEM_MESSAGE_PURPOSE_ENTITY,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_PURPOSE_ENTITY,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:purpose-span-sent-entity-v2-d4:ADXz8d6q",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
    },
    parse_ambiguous_data=True,
)

Q_PURPOSE_CLASSIFICATION = QueryHelper(
    cache_category=QueryCategory.PURPOSE_CLASSIFICATION,
    system_message=prompt.SYSTEM_MESSAGE_PURPOSE_CATEGORY_CLASSIFICATION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_PURPOSE_CATEGORY,
    llm_model="ft:gpt-4o-2024-08-06:rui:purpose-class-sent-purpose-v2-d4:AEP9aVII",
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
