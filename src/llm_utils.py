import json
from copy import deepcopy
import sklearn.metrics as sklm
import datetime
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv
import openai
from openai import OpenAI
from . import annotation_utils as a_utils
from .message_templates import (
    USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION,
    USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2,
)
from .utils import path_default

load_dotenv()
client = OpenAI()

OUT_PATH = Path('../out/')

F_JOB_DESC = 'job_desc.json'  # Contains the job description, i.e. description of the job to submit (*before* submitting)
F_JOB_INFO = 'job_info.json'  # Contains the job information, i.e. information for the submitted job (*after* submitting)
F_EVAL_DESC = 'desc.json' # Contains the description of the evaluation job

F_LAST_EVAL = 'last_evaluation'
F_LAST_FINE_TUNE = 'last_fine_tune'

SYSTEM_MESSAGE = 'You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate entities in it.'


def as_training_data_for_data_span_of_segment(data_entities_of_segments):
    # Prompt is adpted and very briefly modified based on Vlad's original prompt. It may not be the best one as usage is different.
    prompt_template = USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION
    data_template = {
        "messages": [
            {"role": "system", "content": "You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate entities in it."},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}
    
    data_list = []

    for segment in data_entities_of_segments:
        prompt = prompt_template.format(segment=segment["segment"])
        answers = segment["entities"]
        # Keep only the text in answers
        answers = [a["text"] for a in answers]
        data = deepcopy(data_template)
        data["messages"][1]["content"] = prompt
        data["messages"][2]["content"] = json.dumps(answers)
        data_list.append(data)
    return data_list


def as_training_data_for_data_span_of_sentence(data_entities_of_sentences):
    # Prompt is adpted and very briefly modified based on Vlad's original prompt. It may not be the best one as usage is different.
    prompt_template = USER_MESSAGE_TEMPLATE_DATA_ENTITY_RECOGNITION_2
    data_template = {
        "messages": [
            {"role": "system", "content": "You are an annotation expert. You will be given a segment of a privacy policy of a web or mobile application, and will be asked to annotate entities in it."},
            {"role": "user", "content": None},
            {"role": "assistant", "content": None},
        ]}
    
    data_list = []

    for segment in data_entities_of_sentences:
        prompt = prompt_template.format(**segment)
        answers = segment["entities"]
        # Keep only the text in answers
        answers = [a["text"] for a in answers]
        data = deepcopy(data_template)
        data["messages"][1]["content"] = prompt
        data["messages"][2]["content"] = json.dumps(answers)
        data_list.append(data)
    return data_list


def fine_tune_with_data(all_data, training_set_indices, validation_set_indices, annotation_data_path, annotation_data_def, basemodel='gpt-4o-mini-2024-07-18', fine_tune_args={}):
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
        
    with open(validation_data_file, 'w') as f:
        f.write(to_jsonl(validation_set))
        
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
def reconstruct_data_sets(job_desc_dir=None):
    with open(job_desc_dir / F_JOB_DESC) as f:
        job_desc = json.load(f)
        
    data_entities = a_utils.load_data_entities_of_segments(job_desc['annotation_data_path'], job_desc['annotation_data_def'])
    all_data = as_training_data_for_data_span_of_segment(data_entities)
        
    training_set = [all_data[i] for i in job_desc['training_set_indices']]
    validation_set = [all_data[i] for i in job_desc['validation_set_indices']]
    test_set = [all_data[i] for i in set(range(len(all_data))) - set(job_desc['training_set_indices']) - set(job_desc['validation_set_indices'])]

    return training_set, validation_set, test_set


@pd(F_LAST_FINE_TUNE)
def load_eval_info(job_desc_dir=None):
    training_set, validation_set, test_set = reconstruct_data_sets(job_desc_dir)
    
    stat = await_fine_tune_finish_and_clean_up(job_desc_dir)
    fine_tuned_model_id = stat.fine_tuned_model
    
    return training_set, validation_set, test_set, fine_tuned_model_id


def query_llm(model: str, messages_list, correct_outputs=[], dir_name=None):
    '''
    Query the LLM, and also automatically saves the responses in case needed further
    
    @param correct_outputs: list of additional outputs to be saved along with the input and output; useful to store metadata or other forms of the correct output data
    @param dir_name: the name of the directory to save the outputs; if not provided, a timestamped directory name will be created; it will be relative to `OUT_PATH`
    '''
    if not dir_name:
        dir_name = f"eval-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{model}"
    dir_path = OUT_PATH / dir_name
    dir_path.mkdir()
    
    fl = OUT_PATH / F_LAST_EVAL
    if fl.exists(follow_symlinks=False): fl.unlink()
    fl.symlink_to(dir_path)
    
    desc_file = dir_path / 'desc.json'
    with open(desc_file, 'w') as f:
        json.dump({
            'model': model,
        }, f)
    
    model_output_list = []
    for i, messages in enumerate(tqdm(messages_list)):
        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )
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


@pd(F_LAST_EVAL)
def load_saved_llm_queries(dir_name=None):
    dir_path = OUT_PATH / dir_name
    desc = None
    queries = []
    for file_path in dir_path.iterdir():
        with open(file_path, 'r') as f:
            data = json.load(f)
            if file_path.name == F_EVAL_DESC:
                desc = data
            else:
                queries.append(data)
    return desc, queries


def precision_accuracy_f1(expected, predicted):
    expected = set(expected)
    predicted = set(predicted)
    precision = len(expected.intersection(predicted)) / len(predicted) if predicted else 0 if expected else 1
    recall = len(expected.intersection(predicted)) / len(expected) if expected else 0 if predicted else 1
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0 if expected or predicted else 1
    return precision, recall, f1
    # return sklm.precision_recall_fscore_support(expected, predicted)[:3]