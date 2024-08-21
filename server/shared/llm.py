import base64
import datetime
import hashlib
import json
import os
import re
from enum import Enum, auto

import backoff
import openai
from dotenv import load_dotenv
from jsonschema.validators import validate
from openai import AzureOpenAI, OpenAI
from jinja2 import Template
import yaml
import inspect
from concurrent.futures import ThreadPoolExecutor, as_completed

from server.generation_recipes.read_schemas import bundle_schemas
from server.shared.dalle import DalleClient

load_dotenv()


OPENAI_API_TYPE = os.getenv('OPENAI_API_TYPE').lower()


class ApiType(Enum):
    OPENAI = "openai"
    AZURE = "azure"


class ModelType(Enum):
    GPT_4_OMNI = auto()
    GPT_4_MINI = auto()
    GPT_4_VISION = auto()
    GPT_35_TURBO = auto()


OPENAI_MODELS = {
    ModelType.GPT_4_OMNI: "gpt-4o-2024-08-06",
    ModelType.GPT_4_MINI: "gpt-4o-mini",
    ModelType.GPT_4_VISION: "gpt-4-turbo",
    ModelType.GPT_35_TURBO: "gpt-3.5-turbo"
}

OPENAI_AZURE_MODELS = {
    ModelType.GPT_4_OMNI: "gpt-4o",
    ModelType.GPT_4_MINI: "gpt-4o-mini",
    ModelType.GPT_4_VISION: "gpt-4v",
    ModelType.GPT_35_TURBO: "gpt-35-turbo"
}


def create_llm_client():
    if OPENAI_API_TYPE == ApiType.AZURE.value:
        return AzureOpenAI(
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version="2024-02-01"
        )
    elif OPENAI_API_TYPE == ApiType.OPENAI.value:
        return OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )
    else:
        raise ValueError("Invalid API type. Please set OPENAI_API_TYPE to 'openai' or 'azure' in the .env file.")


def get_model_name(model_type):
    if OPENAI_API_TYPE == ApiType.AZURE.value:
        return OPENAI_AZURE_MODELS[model_type]
    elif OPENAI_API_TYPE == ApiType.OPENAI.value:
        return OPENAI_MODELS[model_type]
    else:
        raise ValueError("Invalid API type. Please set OPENAI_API_TYPE to 'openai' or 'azure' in the .env file.")


@backoff.on_exception(backoff.expo, openai.RateLimitError, max_time=60)
def completions_with_backoff(client, **kwargs):
    return client.chat.completions.create(**kwargs)


def create_prompt_from_template(file_path, **kwargs):
    with open(file_path, 'r') as file:
        template_string = file.read()

    template = Template(template_string)
    rendered_template = template.render(kwargs)

    return rendered_template


def extract_tool_metadata(tool):
    doc = tool.__doc__
    if doc:
        metadata = yaml.safe_load(doc)
        return metadata
    return {}


def generate_tool_description(tool):
    metadata = extract_tool_metadata(tool)
    tool_description = {
        "type": "function",
        "function": {
            "name": tool.__name__,
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


def execute_tool(tool, tool_args, allowed_tools):
    tool_name = tool.__name__
    tool_params = inspect.signature(tool).parameters
    call_args = {param: tool_args[param] for param in tool_params if param in tool_args}
    result = tool(**call_args)
    return tool_name, result


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


def parse_css(content):
    pattern = re.compile(r'```css(.*?)```', re.DOTALL)
    matches = pattern.findall(content)
    css_blocks = [match.strip() for match in matches]
    return css_blocks


class LlmClient:
    def __init__(self, model=ModelType.GPT_4_OMNI, system_prompt=None):
        self.client = create_llm_client()
        self.model = get_model_name(model)
        self.system_prompt = system_prompt

    def get_completions(self, prompt, image_list=None, max_tokens=4096, temperature=1.0, json_output=False, json_schema=None, tools=None):
        messages = []
        allowed_tools = {}

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

        request_params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if json_output:
            if json_schema:
                print("Using JSON schema mode")
                if OPENAI_API_TYPE == ApiType.AZURE.value:
                    print("Azure API does not support JSON schema. Fallback to JSON object.")
                    request_params["response_format"] = {"type": "json_object"}
                else:
                    request_params["response_format"] = {"type": "json_schema", "json_schema": {"strict": True, "schema": json_schema, "name": "json_schema"}}
            else:
                print("Using JSON object mode")
                request_params["response_format"] = {"type": "json_object"}

        if tools:
            print("Configuring tools...")
            tool_descriptions = [generate_tool_description(tool) for tool in tools] if tools else []
            allowed_tools = {tool.__name__: tool for tool in tools} if tools else {}
            request_params["tools"] = tool_descriptions
            request_params["tool_choice"] = "auto"

        response = completions_with_backoff(self.client, **request_params)

        while response.choices[0].message.tool_calls:
            print(f"Calling tools...")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")

            messages.append(response.choices[0].message)

            with ThreadPoolExecutor() as executor:
                future_to_tool_call = {
                    executor.submit(execute_tool, allowed_tools[tool_call.function.name], json.loads(tool_call.function.arguments), allowed_tools): tool_call.id
                    for tool_call in response.choices[0].message.tool_calls
                }

                for future in as_completed(future_to_tool_call):
                    tool_call_id = future_to_tool_call[future]
                    try:
                        tool_name, result = future.result()
                    except Exception as exc:
                        result = str(exc)
                        tool_name = "unknown"

                    print(f"Tool: {tool_name}")
                    print(f"Result: {result}")

                    messages.append(
                        {
                            "tool_call_id": tool_call_id,
                            "role": "tool",
                            "name": tool_name,
                            "content": str(result),
                        }
                    )

            response = completions_with_backoff(self.client, **request_params)

        print(f"Finish reason: {response.choices[0].finish_reason}")
        print(f"Completion tokens: {response.usage.completion_tokens}")
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")

        content = response.choices[0].message.content

        if json_output and "json_schema" in request_params["response_format"]:
            print("Validating JSON schema...")
            validate(instance=json.loads(content), schema=json_schema)

        return content


if __name__ == "__main__":
    llm = LlmClient(model=ModelType.GPT_4_OMNI)
    json_schema = bundle_schemas("../generation_recipes/component_schemas/page.json")

    def generate_image(prompt):
        """
        description: Generate an image URL based on the provided prompt.
        parameters:
          prompt:
            type: string
            description: The prompt for generating the image.
        returns:
          type: string
          description: The image URL generated based on the prompt.
        """
        return 'https://www.example.com/image.png'

    def add_numbers(a, b):
        """
        description: Add two numbers.
        parameters:
            a:
                type: number
                description: The first number.
            b:
                type: number
                description: The second number.
        return:
            type: number
            description: The sum of the two numbers.
        """
        print(f"Adding {a} and {b}")
        return a + b

    result_schema = {
        "type": "object",
        "properties": {
            "imageUrl": {
                "type": "string",
                "description": "The image URL of the result."
            },
            "result": {
                "type": "number",
                "description": "The sum of the two numbers."
            }
        },
        "required": ["imageUrl", "result"],
        "additionalProperties": False
    }

    prompt = f'''
        You are an experienced web developer tasked with creating a new web page.

        Your task is to generate the JSON structure for the web page on the given requirements.
        You MUST generate images URLs for the images and include them in the JSON structure.
        Always use the tool to generate the image URLs.

        {json.dumps(json_schema, indent=2)}

        Please provide the JSON structure for the web page:
    '''
    response = llm.get_completions(prompt, json_output=True, json_schema=json_schema, tools=[add_numbers, generate_image])

    print(response)
