import json
from copy import deepcopy
import sklearn.metrics as sklm
import datetime
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv
import openai
from openai import OpenAI
import time
import logging
import re
import chromadb
import os
from . import annotation_utils as a_utils
from .utils import path_default
from .env import (
    BRAT_DATA_PATH,
    F_DATA_CATEGORY_DEFINITION,
)

load_dotenv()
client = OpenAI()
# chroma_client = chromadb.HttpClient(host=os.environ['CHROMADB_HOST'], port=os.environ.get('CHROMADB_PORT', 8000))

OUT_PATH = Path('../out/')

F_JOB_DESC = 'job_desc.json'  # Contains the job description, i.e. description of the job to submit (*before* submitting)
F_JOB_INFO = 'job_info.json'  # Contains the job information, i.e. information for the submitted job (*after* submitting)
F_EVAL_DESC = 'desc.json' # Contains the description of the evaluation job
F_EVAL_AUX = {
    'response': 'response.jsonl',
    'batch_data': 'batch_data.jsonl',
    'correct_outputs': 'correct_outputs.json',
    'desc': 'desc.json',
}

F_LAST_EVAL = 'last_evaluation'
F_LAST_FINE_TUNE = 'last_fine_tune'


SEED = 10000
TEMPERATURE = 0
MAX_TOKENS = 1000


logger = logging.getLogger(__name__)


def fine_tune_with_data(all_data, training_set_indices, validation_set_indices, annotation_data_path=BRAT_DATA_PATH, annotation_data_def=F_DATA_CATEGORY_DEFINITION, basemodel='gpt-4o-mini-2024-07-18', fine_tune_args={}, desc=None):
    job_desc_dir = OUT_PATH / f"fine_tune-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{basemodel}"
    job_desc_dir.mkdir()

    fl = OUT_PATH / F_LAST_FINE_TUNE
    if fl.exists(follow_symlinks=False): fl.unlink()
    fl.symlink_to(job_desc_dir)

    training_set = [all_data[i] for i in training_set_indices]
    validation_set = [all_data[i] for i in validation_set_indices]
    test_set = [all_data[i] for i in set(range(len(all_data))) - set(training_set_indices) - set(validation_set_indices)]

    def to_jsonl(data_set):
        content = ''
        for data in data_set:
            p = json.dumps(data)
            content += p + '\n'
        return content

    def us(msg):  # Update Status
        print(msg)

    us('Constructing training and validation data files (locally)...')

    training_data_file = job_desc_dir / 'training_data.jsonl'
    validation_data_file = job_desc_dir / 'validation_data.jsonl'

    with open(training_data_file, 'w') as f:
        f.write(to_jsonl(training_set))
        f.flush()

    with open(validation_data_file, 'w') as f:
        f.write(to_jsonl(validation_set))
        f.flush()

    us('Uploading training and validation data files...')

    training_data_remote_file = client.files.create(
        file=open(training_data_file, "rb"),
        purpose="fine-tune"
    )

    validation_data_remote_file = client.files.create(
        file=open(validation_data_file, "rb"),
        purpose="fine-tune"
    )

    us('Data files uploading (API calls returned).')

    us('Creating fine-tuning job...')

    final_fine_tune_args = {
        'model': basemodel,
        'training_file': training_data_remote_file.id,
        'validation_file': validation_data_remote_file.id,
        "integrations": [
            {
                "type": "wandb",
                "wandb": {
                    "project": "renyuneyun-university-of-oxford",
                    "tags": ["project:tag", "lineage"]
                }
            }
        ],
        **fine_tune_args,
    }

    fine_tune_job = client.fine_tuning.jobs.create(**final_fine_tune_args)

    us('Created fine-tuning job.')

    job_desc_file = job_desc_dir / F_JOB_DESC
    with open(job_desc_file, 'w') as f:
        job_desc = {
            'job_id': fine_tune_job.id,
            'fine_tune_args': final_fine_tune_args,
            'annotation_data_path': annotation_data_path,
            'annotation_data_def': annotation_data_def,
            'training_set_indices': training_set_indices,
            'validation_set_indices': validation_set_indices,
        }
        if desc:
            job_desc['description'] = desc
        json.dump(job_desc, f)

    update_fine_tune_job_info(job_desc_dir, fine_tune_job.id)

    us('Job description saved.')

    return job_desc_dir, fine_tune_job, test_set


def pd(some_dir):
    return path_default(some_dir, OUT_PATH)


@pd(F_LAST_FINE_TUNE)
def get_fine_tune_job_id(job_desc_dir=None):
    with open(job_desc_dir / 'job_desc.json') as f:
        job_desc = json.load(f)
    fine_tune_job_id = job_desc['job_id']
    return fine_tune_job_id


@pd(F_LAST_FINE_TUNE)
def update_fine_tune_job_info(job_desc_dir=None, fine_tune_job_id=None):
    if not fine_tune_job_id:
        fine_tune_job_id = get_fine_tune_job_id(job_desc_dir)
    stat = client.fine_tuning.jobs.retrieve(fine_tune_job_id)

    job_info_file = job_desc_dir / F_JOB_INFO
    with open(job_info_file, 'w') as f:
        json.dump(stat.to_dict(), f)

    return job_info_file, stat


@pd(F_LAST_FINE_TUNE)
def await_fine_tune_finish_and_clean_up(job_desc_dir=None, wait_for_job_completion=True):
    with open(job_desc_dir / 'job_desc.json') as f:
        job_desc = json.load(f)

    fine_tune_job_id = job_desc['job_id']

    previous_files = client.files.list(purpose="fine-tune")

    def delete_remote_file_if_exists(file_id):
        for file in previous_files:
            if file.id == file_id:
                client.files.delete(file_id=file_id)
                break

    while True:
        job_info_file, stat = update_fine_tune_job_info(job_desc_dir, fine_tune_job_id)

        if stat.finished_at:
            training_file_id = job_desc['fine_tune_args']['training_file']
            validation_file_id = job_desc['fine_tune_args']['validation_file']
            delete_remote_file_if_exists(training_file_id)
            delete_remote_file_if_exists(validation_file_id)

        if not wait_for_job_completion or stat.finished_at:
            break

    return stat


@pd(F_LAST_FINE_TUNE)
def reconstruct_data_sets(job_desc_dir=None, all_data=None):
    with open(job_desc_dir / F_JOB_DESC) as f:
        job_desc = json.load(f)

    if not all_data:
        data_entities = a_utils.load_data_entities_of_segments(job_desc['annotation_data_path'], job_desc['annotation_data_def'])
        all_data = as_training_data_for_data_span_of_segment(data_entities)

    training_set = [all_data[i] for i in job_desc['training_set_indices']]
    validation_set = [all_data[i] for i in job_desc['validation_set_indices']]
    test_set = [all_data[i] for i in set(range(len(all_data))) - set(job_desc['training_set_indices']) - set(job_desc['validation_set_indices'])]

    return training_set, validation_set, test_set


@pd(F_LAST_FINE_TUNE)
def load_fine_tune_description(job_desc_dir=None):
    with open(job_desc_dir / F_JOB_DESC) as f:
        job_desc = json.load(f)
    return job_desc['description']


@pd(F_LAST_FINE_TUNE)
def load_eval_info(job_desc_dir=None, all_data=None):
    training_set, validation_set, test_set = reconstruct_data_sets(job_desc_dir, all_data)

    stat = await_fine_tune_finish_and_clean_up(job_desc_dir)
    fine_tuned_model_id = stat.fine_tuned_model

    return training_set, validation_set, test_set, fine_tuned_model_id


RE_QUERY_RESULTS = re.compile(r'^(\d+)\.json$')


def query_llm(model: str, messages_list, correct_outputs=[], dir_name=None, desc=None, batch=True):
    '''
    Query the LLM, and also automatically saves the responses in case needed further

    @param correct_outputs: list of additional outputs to be saved along with the input and output; useful to store metadata or other forms of the correct output data
    @param dir_name: the name of the directory to save the outputs; if not provided, a timestamped directory name will be created; it will be relative to `OUT_PATH`
    '''
    if not dir_name:
        dir_name = f"eval-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{model}"
    dir_path = OUT_PATH / dir_name
    existing_queries = []
    if dir_path.exists():
        for file_path in dir_path.iterdir():
            if file_path.name in F_EVAL_AUX.values():
                continue
            if m := RE_QUERY_RESULTS.match(file_path.name):
                existing_queries.append(int(m.group(1)))
    else:
        dir_path.mkdir()

    fl = OUT_PATH / F_LAST_EVAL
    if fl.exists(follow_symlinks=False): fl.unlink()
    fl.symlink_to(dir_path)

    desc_file = dir_path / 'desc.json'
    d = {
        'model': model,
        }
    if desc:
        d['description'] = desc

    def to_jsonl(data_list):
        content = ''
        for data in data_list:
            p = json.dumps(data)
            content += p + '\n'
        return content

    if batch:
        batch_input_list = []
        for i, messages in enumerate(tqdm(messages_list, desc='Constructing batch data', leave=False)):
            data_item = {
                'custom_id': f"request-{i}",
                'method': 'POST',
                'url': '/v1/chat/completions',
                'body': {
                    'model': model,
                    'temperature': TEMPERATURE,
                    'seed': SEED,
                    'messages': messages,
                    'max_tokens': MAX_TOKENS,
                }
            }
            batch_input_list.append(data_item)
        batch_input_file = dir_path / 'batch_data.jsonl'
        with open(batch_input_file, 'w') as f:
            f.write(to_jsonl(batch_input_list))
            f.flush()
        batch_input_file_remote = client.files.create(
            file=open(batch_input_file, "rb"),
            purpose="batch"
        )

        if correct_outputs:
            correct_output_out = {}
            for i, correct_output in enumerate(correct_outputs):
                correct_output_out[f"request-{i}"] = correct_output
            correct_output_file = dir_path / 'correct_outputs.json'
            with open(correct_output_file, 'w') as f:
                json.dump(correct_output_out, f)
                f.flush()

        batch_job = client.batches.create(
            input_file_id=batch_input_file_remote.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": desc
            }
        )

        d['batch_input_file_id'] = batch_input_file_remote.id
        d['batch_job_id'] = batch_job.id
        with open(desc_file, 'w') as f:
            json.dump(d, f)

        return dir_name, batch_job
    else:
        with open(desc_file, 'w') as f:
            json.dump(d, f)
        model_output_list = []
        for i, messages in enumerate(tqdm(messages_list)):
            if i in existing_queries:
                continue
            query_counter = 0
            while True:
                try:
                    completion = client.chat.completions.create(
                        model=model,
                        temperature=TEMPERATURE,
                        seed=SEED,
                        max_tokens=MAX_TOKENS,
                        messages=messages
                    )
                    break
                except openai.RateLimitError as e:
                    query_counter += 1
                    if query_counter >= 3:
                        logger.error(f"LLM query (at dir <{dir_name}> ) reached rate limit {query_counter}-th time. Won't retry anymore. Error message: {e}")
                        raise e
                    logger.warning(f"LLM query reached rate limit {query_counter}-th time. Will wait and retry. Error message: {e}")
                    time.sleep(90)
            model_output = completion.choices[0].message
            output_file_path = dir_path / f'{i}.json'
            output = {
                'input': messages,
                'output': model_output.content
            }
            if i < len(correct_outputs):
                output['correct_output'] = correct_outputs[i]
            with open(output_file_path, 'w') as f:
                json.dump(output, f)
            model_output_list.append(output)
        return dir_name, model_output_list


def wait_for_batch_job_finish(batch_job_id):
    while True:
        job = client.batches.retrieve(batch_job_id)
        if job.status not in {'validating', 'in_progress', 'finalizing', 'cancelling'}:
            break
        time.sleep(10)
    return job


def _retrieve_batch_job_results(batch_job):
    if isinstance(batch_job, str):
        batch_job = wait_for_batch_job_finish(batch_job)
    else:
        batch_job = wait_for_batch_job_finish(batch_job.id)
    output_file_id = batch_job.output_file_id
    file_response = client.files.content(output_file_id)
    return file_response.text


@pd(F_LAST_EVAL)
def retrieve_batch_query_result(dir_name=None):
    dir_path = OUT_PATH / dir_name
    with open(dir_path / 'desc.json') as f:
        desc = json.load(f)
    batch_job_id = desc['batch_job_id']
    response = _retrieve_batch_job_results(batch_job_id)
    with open(dir_path / 'response.jsonl', 'w') as f:
        f.write(response)


@pd(F_LAST_EVAL)
def combine_batch_query_result(dir_name=None):
    dir_path = OUT_PATH / dir_name
    with open(dir_path / 'batch_data.jsonl') as f:
        input_message = {}
        batch_data = [json.loads(line) for line in f.readlines()]
        for data in batch_data:
            custom_id = data['custom_id']
            messages = data['body']['messages']
            input_message[custom_id] = messages
    with open(dir_path / 'response.jsonl') as f:
        response_message = {}
        responses_raw = f.readlines()
        for item in responses_raw:
            response = json.loads(item)
            custom_id = response['custom_id']
            message = response['response']['body']['choices'][0]['message']['content']
            response_message[custom_id] = message
    correct_outputs = {}
    correct_output_file = dir_path / 'correct_outputs.json'
    if correct_output_file.exists():
        with open(correct_output_file) as f:
            correct_outputs = json.load(f)
    for k, messages in input_message.items():
        try:
            output = response_message[k]
        except KeyError:
            print(f"Message with custom_id {k} not found in response")
        output_file_path = dir_path / f'{k}.json'
        output = {
            'input': messages,
            'output': output
        }
        if k in correct_outputs:
            output['correct_output'] = correct_outputs[k]
        with open(output_file_path, 'w') as f:
            json.dump(output, f)


@pd(F_LAST_EVAL)
def load_saved_llm_queries(dir_name=None):
    dir_path = OUT_PATH / dir_name
    desc = None
    queries = []
    for file_path in dir_path.iterdir():
        if file_path.name in F_EVAL_AUX.values() and file_path.name != F_EVAL_DESC:
            continue
        if file_path.is_dir():
            continue
        with open(file_path, 'r') as f:
            data = json.load(f)
            if file_path.name == F_EVAL_DESC:
                desc = data
            else:
                queries.append(data)
    return desc, queries


def clear_server_data(types = ["fine-tune", 'batch']):
    for t in tqdm(types, 'Clearing server data', leave=False):
        previous_files = client.files.list(purpose=t)
        for file in tqdm(previous_files, desc=f'Clearing {t} data', leave=False):
            client.files.delete(file.id)


def query_similarity(collection_name: str, queries, correct_outputs=[], dir_name=None, desc=None, n_results=None):
    '''
    Query Chroma for similarity-based classification (of data types and purposes).
    Saves result similar to `query_llm`, but with its different description.

    @param correct_outputs: list of additional outputs to be saved along with the input and output; useful to store metadata or other forms of the correct output data
    @param dir_name: the name of the directory to save the outputs; if not provided, a timestamped directory name will be created; it will be relative to `OUT_PATH`
    @param n_results: number of results to return for each query; if None, directly use the only result (removing brackets); otherwise, return a list of results for each query
    '''
    if not dir_name:
        dir_name = f"eval-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{collection_name}"
    dir_path = OUT_PATH / dir_name
    existing_queries = []
    if dir_path.exists():
        for file_path in dir_path.iterdir():
            if file_path.name in F_EVAL_AUX.values():
                continue
            if m := RE_QUERY_RESULTS.match(file_path.name):
                existing_queries.append(int(m.group(1)))
    else:
        dir_path.mkdir()

    fl = OUT_PATH / F_LAST_EVAL
    if fl.exists(follow_symlinks=False): fl.unlink()
    fl.symlink_to(dir_path)

    desc_file = dir_path / 'desc.json'
    d = {
        'method': 'Similarity-based retrieval',
        'collection': collection_name,
        }
    if desc:
        d['description'] = desc
    if n_results:
        d['n_results'] = n_results

    collection = chroma_client.get_collection(collection_name)

    with open(desc_file, 'w') as f:
        json.dump(d, f)
    model_output_list = []
    for i, messages in enumerate(tqdm(queries)):
        if i in existing_queries:
            continue

        resp = collection.query(
            query_texts = messages,
            n_results = n_results,
        )

        original_output = resp['metadatas']
        if n_results:
            model_output = [[x['name'] for x in lst] for lst in original_output]
        else:
            model_output = [x[0]['name'] for x in original_output]

        output_file_path = dir_path / f'{i}.json'
        output = {
            'input': messages,
            'output': model_output
        }
        if i < len(correct_outputs):
            output['correct_output'] = correct_outputs[i]
        with open(output_file_path, 'w') as f:
            json.dump(output, f)
        model_output_list.append(output)
    return dir_name, model_output_list
