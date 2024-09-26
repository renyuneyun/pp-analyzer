import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, Callable
from . import prompt
from .external import json_parse


load_dotenv()
client = OpenAI()


def parse(model_output_text: str):
    text, obj = json_parse.try_parse_json_object(model_output_text)
    return obj


class QueryHelper(BaseModel):
    system_message: str
    user_message_template: str
    llm_model: str
    user_message_fn: Optional[Callable] = None

    def run_query(self, data: dict):
        '''
        Run query, and return the parsed result (usually either a list or a dict).
        If anything wrong happens (e.g., API error, parsing error), throw an exception.
        '''
        if self.user_message_fn:
            data = self.user_message_fn(data)
        user_message = self.user_message_template.format(**data)
        completion = client.chat.completions.create(
            model=self.llm_model,
            temperature=0,
            seed=10000,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message}
            ]
        )
        model_output = completion.choices[0].message
        model_output_text = model_output.content
        parsed_result = parse(model_output_text)
        return parsed_result


Q_DATA_ENTITY = QueryHelper(
    system_message=prompt.SYSTEM_MESSAGE_DATA_ENTITY,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_DATA_ENTITY,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:data-entity-sent-data-ver2:A8ycyw3W",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
        "segment": data["segment"],
    },
)

Q_DATA_CLASSIFICATION = QueryHelper(
    system_message=prompt.SYSTEM_MESSAGE_DATA_ENTITY_CLASSIFICATION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_DATA_ENTITY_CLASSIFICATION,
    llm_model="ft:gpt-4o-2024-08-06:rui:data-class-sent-data-v2:A9HochjC",
)

Q_ACTION_RECOGNITION = QueryHelper(
    system_message=prompt.SYSTEM_MESSAGE_ACTION_RECOGNITION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_ACTION_RECOGNITION,
    llm_model="ft:gpt-4o-mini-2024-07-18:rui:action-sent-v2:A9KKKeHG",
    user_message_fn=lambda data: {
        "sentence": data["segment"],
        "segment": data["segment"],
    },
)

Q_RELATION_RECOGNITION = QueryHelper(
    system_message=prompt.SYSTEM_MESSAGE_RELATION_RECOGNITION,
    user_message_template=prompt.USER_MESSAGE_TEMPLATE_RELATION_RECOGNITION,
    llm_model="ft:gpt-4o-2024-08-06:rui:relation-seg-v2:AAmgfsI1",
)
