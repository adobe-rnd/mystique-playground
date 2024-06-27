import base64
import json
import os
import re
from enum import Enum
from dotenv import load_dotenv
from openai import AzureOpenAI
from jinja2 import Template
import yaml
import inspect

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-02-01"
)

class ModelType(Enum):
    GPT_4_OMNI = "gpt-4o"
    GPT_4_VISION = "gpt-4v"
    GPT_35_TURBO = "gpt-35-turbo"


def parse_css(content):
    pattern = re.compile(r'```css(.*?)```', re.DOTALL)
    matches = pattern.findall(content)
    css_blocks = [match.strip() for match in matches]
    return css_blocks


def extract_metadata(func):
    doc = func.__doc__
    if doc:
        metadata = yaml.safe_load(doc)
        return metadata
    return {}


def generate_tool_description(func):
    metadata = extract_metadata(func)
    tool_description = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": metadata.get("description", ""),
            "parameters": {
                "type": "object",
                "properties": {
                    param_name: {
                        "type": param_details["type"],
                        "description": param_details["description"]
                    }
                    for param_name, param_details in metadata.get("parameters", {}).items()
                },
                "required": list(metadata.get("parameters", {}).keys())
            }
        }
    }
    return tool_description


def call_function(func_name, args, allowed_functions):
    if func_name not in allowed_functions:
        raise ValueError(f"Function {func_name} is not allowed.")
    func = allowed_functions[func_name]
    func_params = inspect.signature(func).parameters
    call_args = {param: args[param] for param in func_params if param in args}
    return func(**call_args)


class LlmClient:
    def __init__(self, model=ModelType.GPT_4_OMNI, system_prompt=None):
        self.model = model
        self.system_prompt = system_prompt

    def get_completions(self, prompt, functions, image_list=None, max_tokens=4096, temperature=1.0, json_output=False):
        messages = []

        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.system_prompt,
                    }
                ],
            })

        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                }
            ],
        }
        messages.append(user_message)

        if image_list:
            for image in image_list:
                if isinstance(image, str) and image.startswith('data:image'):
                    # Image is a data URL
                    user_message["content"].append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image
                            }
                        }
                    )
                elif isinstance(image, bytes):
                    # Image is binary data
                    image_encoded_data = base64.b64encode(image).decode('utf-8')
                    user_message["content"].append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_encoded_data}"
                            }
                        }
                    )
                else:
                    raise ValueError("Image must be either a data URL (str) or binary data (bytes)")

        tools = [generate_tool_description(func) for func in functions]
        allowed_functions = {func.__name__: func for func in functions}

        request_params = {
            "model": self.model.value,
            "messages": messages,
            "tools": tools,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1.0,
        }

        if json_output:
            request_params["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**request_params)

        while response.choices[0].finish_reason == "tool_calls":
            messages.append(response.choices[0].message)
            for tool_call in response.choices[0].message.tool_calls:
                print(f"Tool call: {tool_call}")
                func_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                result = call_function(func_name, function_args, allowed_functions)
                print(f"Function: {func_name}")
                print(f"Arguments: {function_args}")
                print(f"Result: {result}")
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": str(result),
                    }
                )
            response = client.chat.completions.create(
                model=self.model.value,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

        print(f"Finish reason: {response.choices[0].finish_reason}")
        print(f"Completion tokens: {response.usage.completion_tokens}")
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")

        return response.choices[0].message.content

def create_prompt_from_template(file_path, **kwargs):
    with open(file_path, 'r') as file:
        template_string = file.read()

    template = Template(template_string)
    rendered_template = template.render(kwargs)

    return rendered_template

def parse_markdown_output(output, lang='html'):
    parsed_data = {}

    code_snippet_pattern = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)

    matches = code_snippet_pattern.findall(output)

    for lang, snippet in matches:
        if not lang:
            lang = 'plain'
        parsed_data[lang] = parsed_data.get(lang, []) + [snippet.strip()]

    if lang in parsed_data:
        return '\n'.join(parsed_data[lang])

    return output


def evaluate_expression(expression: str) -> float:
    """
    description: Evaluate a mathematical expression.
    parameters:
      expression:
        type: string
        description: The mathematical expression to evaluate.
    returns:
      type: float
      description: The result of the evaluated expression.
    """
    return eval(expression)

def another_custom_function(param1: int, param2: str) -> str:
    """
    description: An example of another custom function.
    parameters:
      param1:
        type: integer
        description: The first parameter.
      param2:
        type: string
        description: The second parameter.
    returns:
      type: string
      description: A formatted string combining param1 and param2.
    """
    return f"Combined result: {param1} and {param2}"

llm = LlmClient(ModelType.GPT_4_OMNI)

analysis_prompt = f"""What is 1 + 1 minus 1 multiplied by 2?"""

result = llm.get_completions(analysis_prompt, functions=[evaluate_expression, another_custom_function])

print(result)
