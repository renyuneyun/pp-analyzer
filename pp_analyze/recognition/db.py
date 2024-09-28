from datetime import datetime
from dotenv import load_dotenv
import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.event import listen
from sqlalchemy_utils import database_exists, create_database
import sqlite3
import sqlite_zstd
from sqlmodel import Field, Session, SQLModel, create_engine, select, DateTime
from typing import Optional, Callable
from .utils import dict_hash


load_dotenv()

_CACHE_DIR = Path(os.getenv("LLM_QUERY_CACHE_DIR")) if os.getenv("LLM_QUERY_CACHE_DIR") else None

# class QueryRecord(SQLModel, table=True):
#     __table_args__ = {'extend_existing': True}

#     id: Optional[int] = Field(default=None, primary_key=True)
#     hash_key: str
#     timestamp: str = Field(default_factory=datetime.now().isoformat)
#     model: str
#     temperature: float
#     seed: int
#     max_tokens: int
#     system_message: str
#     user_message: str
#     lm_response: str

#     @classmethod
#     def from_dict(cls, data: dict):
#         query_params = data['query_params']
#         lm_response = data['lm_response']
#         if 'timestamp' in data:
#             timestamp = data['timestamp']
#         return cls(
#             hash_key=dict_hash(query_params),
#             model=query_params["model"],
#             temperature=query_params["temperature"],
#             seed=query_params["seed"],
#             max_tokens=query_params["max_tokens"],
#             system_message=query_params['messages'][0]['content'],
#             user_message=query_params['messages'][1]['content'],
#             lm_response=lm_response,
#         )

#     def to_dict(self):
#         '''
#         Convert back to the query parameters dictionary.
#         Will drop the ID and hash_key fields.
#         '''
#         return {
#             "query_params": {
#                 "model": self.model,
#                 "temperature": self.temperature,
#                 "seed": self.seed,
#                 "max_tokens": self.max_tokens,
#                 "messages": [
#                     {"role": "system", "content": self.system_message},
#                     {"role": "user", "content": self.user_message}
#                 ]
#             },
#             "lm_response": self.lm_response,
#             "timestamp": self.timestamp,
#         }

class QueryRecord(SQLModel, table=True):
    # __table_args__ = {'extend_existing': True}

    id: Optional[int] = Field(default=None, primary_key=True)
    hash_key: str
    query_params: str
    lm_response: str
    timestamp: str = Field(default_factory=datetime.now().isoformat)

    def __init__(self, **data):
        query_params = data['query_params']
        if isinstance(query_params, dict):
            data['query_params'] = json.dumps(query_params)
        else:
            query_params = json.loads(query_params)
        if 'hash_key' not in data:
            data['hash_key'] = dict_hash(query_params)
        super().__init__(**data)

    def query_params_dict(self):
        return json.loads(self.query_params)


engine = None
if _CACHE_DIR is not None:
    db_url = f'sqlite:///{(_CACHE_DIR / "llm_query_cache.sqlite").absolute()}'
    engine = create_engine(db_url)

    SQLModel.metadata.create_all(engine)