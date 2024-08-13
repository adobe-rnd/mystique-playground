import json
import os

from openai import AzureOpenAI
from dotenv import load_dotenv

from server.shared.image import load_image, image_to_data_url

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_DALLE_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_DALLE_ENDPOINT')

MODEL_NAME = "Dalle3"


client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2024-02-01"
)


class DalleClient:
    def __init__(self):
        self.cache = {}

    def generate_image(self, prompt):
        if prompt in self.cache:
            print(f"Cache hit for prompt: {prompt}")
            return self.cache[prompt]
        result = client.images.generate(
            model=MODEL_NAME,
            prompt=prompt,
            n=1
        )
        image_url = json.loads(result.model_dump_json())['data'][0]['url']
        image = load_image(image_url)
        data_url = image_to_data_url(image)
        self.cache[prompt] = data_url
        return image_to_data_url(image)

