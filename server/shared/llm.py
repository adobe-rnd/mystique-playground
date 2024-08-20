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
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    GPT_4_OMNI_MINI = "gpt-4o-mini"
    GPT_4_VISION = "gpt-4v"
    GPT_35_TURBO = "gpt-35-turbo"


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
        self.model = model
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
            "model": self.model.value,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1.0,
        }

        if json_output:
            if json_schema:
                print("Using JSON schema")
                request_params["response_format"] = {"type": "json_schema", "json_schema": json_schema, "strict": True }
            else:
                print("Using JSON object")
                request_params["response_format"] = {"type": "json_object"}

        if tools:
            tool_descriptions = [generate_tool_description(tool) for tool in tools] if tools else []
            allowed_tools = {tool.__name__: tool for tool in tools} if tools else {}
            request_params["tools"] = tool_descriptions

        response = client.chat.completions.create(**request_params)

        while response.choices[0].finish_reason == "tool_calls":
            print(f"Calling tools...")

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
