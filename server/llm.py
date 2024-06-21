import base64
import os
import re
from enum import Enum
from io import BytesIO
from PIL import Image  # Assuming PIL is used for image processing

from dotenv import load_dotenv
from openai import AzureOpenAI
from jinja2 import Template

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


class LlmClient:
    def __init__(self, model=ModelType.GPT_4_OMNI, system_prompt=None):
        self.model = model
        self.system_prompt = system_prompt

    def get_completions(self, prompt, image_list=None, max_tokens=4096, temperature=1.0, json_output=False):
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

        request_params = {
            "model": self.model.value,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        if json_output:
            request_params["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**request_params)

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
