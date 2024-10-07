from datetime import datetime
from dotenv import load_dotenv
import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import event
import sqlite_zstd
from sqlmodel import Field, SQLModel, create_engine
from typing import Optional
from .utils import dict_hash


load_dotenv()

_CACHE_DIR = Path(os.getenv("LLM_QUERY_CACHE_DIR")) if os.getenv("LLM_QUERY_CACHE_DIR") else None


class QueryRecord(SQLModel, table=True):
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


class BatchQueryRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hash_key: str
    query_params: str
    batch_id: str
    batch_custom_id: str
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


def enable_zstd_extension(dbapi_conn, *args):
    dbapi_conn.enable_load_extension(True)
    sqlite_zstd.load(dbapi_conn)
    dbapi_conn.enable_load_extension(False)
    dbapi_conn.execute('pragma journal_mode=WAL;')
    dbapi_conn.execute('pragma auto_vacuum=full;')


def enable_compression(dbapi_conn, *args):
    dbapi_conn.execute('''SELECT
        zstd_enable_transparent('{"table": "queryrecord", "column": "query_params", "compression_level": 19, "dict_chooser": "''a''"}'),
        zstd_enable_transparent('{"table": "queryrecord", "column": "lm_response", "compression_level": 19, "dict_chooser": "''a''"}')
;''')


engine = None
if _CACHE_DIR is not None:
    db_file = _CACHE_DIR / "llm_query_cache.sqlite"
    db_exists = db_file.exists()
    db_url = f'sqlite:///{db_file.absolute()}'
    engine = create_engine(db_url)
    engine.dialect.supports_sane_rowcount = False
    event.listen(engine, 'connect', enable_zstd_extension)
    SQLModel.metadata.create_all(engine)
    if not db_exists:
        dbapi_conn = engine.raw_connection()
        enable_compression(dbapi_conn)
