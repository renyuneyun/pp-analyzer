# Description: JSON cleaning and parsing utilities.
# Modified from https://bigmodel.cn/dev/howuse/jsonformat
# Unknown license; unknown author; unknown date; probably also unknown origin

import json
# import logging
import re
import ast

from json_repair import repair_json

# log = logging.getLogger(__name__)


def try_parse_ast_to_json(function_string: str) -> tuple[str, dict]:
    """
     # 示例函数字符串
    function_string = "tool_call(first_int={'title': 'First Int', 'type': 'integer'}, second_int={'title': 'Second Int', 'type': 'integer'})"
    :return:
    """

    tree = ast.parse(str(function_string).strip())
    ast_info = ""
    json_result = {}
    # 查找函数调用节点并提取信息
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            function_name = node.func.id
            args = {kw.arg: kw.value for kw in node.keywords}
            ast_info += f"Function Name: {function_name}\r\n"
            for arg, value in args.items():
                ast_info += f"Argument Name: {arg}\n"
                ast_info += f"Argument Value: {ast.dump(value)}\n"
                json_result[arg] = ast.literal_eval(value)

    return ast_info, json_result


def try_parse_json_object(input: str) -> tuple[str, dict]:
    """JSON cleaning and formatting utilities."""
    # Sometimes, the LLM returns a json string with some extra description, this function will clean it up.

    result = None
    try:
        # Try parse first
        result = json.loads(input)
    except json.JSONDecodeError:
        # log.info("Warning: Error decoding faulty json, attempting repair")
        pass

    if result:
        return input, result

    _pattern = '```(?:json)?\n(.*)\n```'
    _match = re.search(_pattern, input, re.DOTALL)
    input = _match.group(1) if _match else input
    try:
        result = json.loads(input)
        return input, result
    except json.JSONDecodeError:
        pass

    # Check if the multi-line input has or ends with a JSON object/array, without Markdown code block.
    input = input.strip()
    _patterns = [
        r"(\[.*\{.*\}.*\])",
        r"(\{.*\[.*\].*\})",
        (r"(\{.*\})$", True),
        (r"(\[.*\])$", True),
    ]
    for _pattern in _patterns:
        if isinstance(_pattern, str):
            _pattern, _must_be_end = _pattern, False
        elif len(_pattern) == 2:
            _pattern, _must_be_end = _pattern
        else:
            raise ValueError("Unexpected pattern definition format")
        _match = re.search(_pattern, input, re.DOTALL)
        if _match:
            if _must_be_end and _match.endpos != len(input):
                continue
            input = _match.group(1)
            try:
                result = json.loads(input)
                return input, result
            except json.JSONDecodeError:
                pass

    # Clean up json string.
    input = (
        input.replace("{{", "{")
        .replace("}}", "}")
        .replace('"[{', "[{")
        .replace('}]"', "}]")
        .replace("\\", " ")
        .replace("\\n", " ")
        .replace("\n", " ")
        .replace("\r", "")
        .strip()
    )

    try:
        result = json.loads(input)
        return input, result
    except json.JSONDecodeError:
        pass

    _pattern = r"\{(.*)\}"
    _match = re.search(_pattern, input)
    input = "{" + _match.group(1) + "}" if _match else input

    try:
        result = json.loads(input)
        return input, result
    except json.JSONDecodeError:
        pass

    try:
        result = json.loads(input)
    except json.JSONDecodeError:
        # Fixup potentially malformed json string using json_repair.
        json_info = str(repair_json(json_str=input, return_objects=False))

        # Generate JSON-string output using best-attempt prompting & parsing techniques.
        try:

            if len(json_info) < len(input):
                json_info, result = try_parse_ast_to_json(input)
            else:
                result = json.loads(json_info)

        except json.JSONDecodeError:
            # log.exception("error loading json, json=%s", input)
            return json_info, None
        else:
            if not isinstance(result, dict):
                # log.exception("not expected dict type. type=%s:", type(result))
                return json_info, {}
            return json_info, result
    else:
        return input, result
