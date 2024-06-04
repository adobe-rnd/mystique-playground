import base64
import os
import re
from enum import Enum
from io import BytesIO

import requests
from dotenv import load_dotenv
from openai import AzureOpenAI
from jinja2 import Template

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')

client = AzureOpenAI(
    azure_endpoint = AZURE_OPENAI_ENDPOINT,
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

    def get_completions(self, prompt, image_data_list=None):
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

        if image_data_list:
            for image_data in image_data_list:
                image_encoded_data = base64.b64encode(image_data).decode('utf-8')
                user_message["content"].append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_encoded_data}"
                        }
                    }
                )

        response = client.chat.completions.create(
            model=self.model.value,
            messages=messages,
        )
        return response.choices[0].message.content


def create_prompt_from_template(file_path, **kwargs):
    with open(file_path, 'r') as file:
        template_string = file.read()

    template = Template(template_string)
    rendered_template = template.render(kwargs)

    return rendered_template


def load_image(image_source):
    if image_source.startswith('http://') or image_source.startswith('https://'):
        response = requests.get(image_source)
        image = BytesIO(response.content)
    else:
        with open(image_source, "rb") as image_file:
            image = BytesIO(image_file.read())

    return image.read()


def parse_markdown_output(output):
    parsed_data = {}

    # Regex pattern to match code snippets in Markdown
    code_snippet_pattern = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)

    # Find all matches
    matches = code_snippet_pattern.findall(output)

    # Iterate through matches and add them to the dictionary
    for lang, snippet in matches:
        # If no language is specified, use 'plain'
        if not lang:
            lang = 'plain'
        parsed_data[lang] = parsed_data.get(lang, []) + [snippet.strip()]

    return parsed_data
