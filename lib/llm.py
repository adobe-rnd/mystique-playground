import base64
import os
import re
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


def create_prompt_from_template(file_path, **kwargs):
    with open(file_path, 'r') as file:
        template_string = file.read()

    template = Template(template_string)
    rendered_template = template.render(kwargs)

    return rendered_template


def load_image_and_convert_to_data_url(image_path):
    with open(image_path, "rb") as image:
        image_base64 = base64.b64encode(image.read()).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"


def get_text_and_image_completions(prompt, image_data = None):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                }
            ],
        },
    ]

    if image_data:
        image_encoded_data = base64.b64encode(image_data).decode('utf-8')
        messages[0]["content"].append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_encoded_data}"
                }
            }
        )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return response.choices[0].message.content


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
