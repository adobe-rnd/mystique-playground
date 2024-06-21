import base64
import random
import string
import traceback
import json

import asyncio
import os
from datetime import datetime

from flask import Flask, Response, request, jsonify, make_response, send_from_directory
import threading
import queue

from flask_cors import CORS

from server.db import JsCodeInjections
from server.generation_strategies.base_strategy import Action, StatusMessage
from server.html_utils import compress_html, decompress_html
from server.llm import LlmClient, ModelType, parse_markdown_output
from server.strategy_loader import load_generation_strategies

class AssistantServer:
    def __init__(self):
        self.app = Flask(__name__)
        self._register_routes()
        CORS(self.app)

    def _register_routes(self):
        self.app.add_url_rule('/assistant', view_func=self.process_assistant_request, methods=['POST'])
        self.app.add_url_rule('/suggest-prompts', view_func=self.suggest_prompts, methods=['POST'])
        self.app.add_url_rule('/autocomplete', view_func=self.autocomplete, methods=['POST'])

    def process_assistant_request(self):
        try:
            data = request.get_json()

            prompt = data.get('prompt')
            context_html = data.get('context')
            # selected_htmls = data.get('selection')
            screenshot_data_url = data.get('screenshot')

            print(f'Prompt: {prompt}')
            print(f'Context HTML: {context_html}')
            # for selected_html in selected_htmls:
            #     print(f'Selection HTML: {selected_html}')

            # Create the screenshots directory if it doesn't exist
            screenshots_dir = 'screenshots'
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            # Decode the base64 image
            if screenshot_data_url:
                header, encoded = screenshot_data_url.split(',', 1)
                screenshot_data = base64.b64decode(encoded)

                # Generate a filename with date and time
                current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
                filename = f'screenshot_{current_time}_{random_string}.png'
                screenshot_path = os.path.join(screenshots_dir, filename)

                # Save the screenshot to a file
                with open(screenshot_path, 'wb') as screenshot_file:
                    screenshot_file.write(screenshot_data)

                print(f'Screenshot saved at: {screenshot_path}')
            else:
                print('No screenshot data received')

            # context_compression_result = compress_html(context_html, replace_urls=True)
            # compressed_html = context_compression_result['compressed_html']
            # url_mapping = context_compression_result['url_mapping']
            # print(f'Compressed HTML: {compressed_html}')
            # print("Compression Ratio (context): {:.2f}%".format(context_compression_result['compression_ratio']))

            # compressed_selected_htmls = []
            # for selected_html in selected_htmls:
            #     selection_compression_result = compress_html(selected_html, replace_urls=True, existing_url_mapping=url_mapping)
            #     compressed_selected_htmls.append(selection_compression_result['compressed_html'])
            #     print(f'Compressed Selection HTML: {selection_compression_result["compressed_html"]}')
            #     print("Compression Ratio (selection): {:.2f}%".format(selection_compression_result['compression_ratio']))

            # selection_htmls = '\n'.join(map(lambda x: f"SELECTED_HTML_FRAGMENT:\n{x}\n", compressed_selected_htmls))

            system_prompt = f"""
                You are a professional web developer.
                You are given a task to make changes to the provided HTML.
                
                You MUST use inline CSS for any styling changes.Do not use tags or classes.
                You MUST output only the modified version of the HTML.            
                
                Do not change image URLs.
                Do not make unnecessary changes.
                
                Use !important in generated inline CSS rules.
                Try to avoid changing the structure of the HTML.
            """

            llm = LlmClient(ModelType.GPT_4_OMNI, system_prompt=system_prompt)

            prompt = f"""
                For the provided HTML, make the following changes:
                
                {prompt}
                
                ```HTML```:
                {context_html}
            """

            print(f'Prompt: {prompt}')

            if screenshot_data_url:
                image_list = [screenshot_data_url]
            else:
                image_list = []

            llm_response = llm.get_completions(prompt, image_list=image_list, temperature=0.0)

            new_html = parse_markdown_output(llm_response, lang='html')

            # decompressed_html = decompress_html(new_html, context_compression_result['url_mapping'])

            # print(f'Reconstructed HTML: {decompressed_html}')

            return jsonify({"html": new_html})
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400

    def suggest_prompts(self):
        try:
            data = request.get_json()
            context_html = data.get('context')

            print(f'Context HTML: {context_html}')

            system_prompt = """
                You are a professional web designer expected to output suggestions for improving the provided HTML.

                Do not suggest changes that would require changing JavaScript.
                Do not suggest to change URLs or links.
                Do not suggest refactoring or restructuring the HTML or CSS.
                Do not suggest animations or dynamic effects.
                Do not use the same suggestion twice.
                Do not offer suggestions that are too similar to each other.
                Do not offer empty suggestions.
                Do not put commas at the end of suggestions.

                Do not output any bullet points or lists.
                Do not use markdown.

                Each suggestion should be up to 12 words.
                Use imperative language.
                Start each sentence with a verb (e.g., "Make the button blue").

                You MUST output suggestions in JSON format as follows:
                {
                    "suggestions": [
                        "Suggestion 1",
                        "Suggestion 2",
                        "Suggestion 3"
                    ]
                }
            """

            llm = LlmClient(ModelType.GPT_4_OMNI, system_prompt=system_prompt)

            prompt = f"""
                Based on the provided HTML, suggest 3 changes to improve the visual appearance, layout, and styling.
                
                {context_html}
            """

            print(f'Prompt: {prompt}')

            llm_response = llm.get_completions(prompt, json_output=True, max_tokens=512)
            json_response = json.loads(llm_response)
            suggestions = json_response.get('suggestions', [])

            return jsonify({"suggestions": suggestions})

        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400

    def autocomplete(self):
        try:
            data = request.get_json()
            prompt = data.get('prompt')
            print(f'Prompt: {prompt}')

            system_prompt = """
                        You are a text completion model.
                        Complete the given sentences with a coherent and appropriate continuation.
                        Keep the same style and tone as the input.
                        Keep the output as short as possible.
                        Output only the completion part of the sentence.
                        Use web design and linguistic vocabulary and concepts.
                        Complete sentences in a way that is relevant to the context.
                        
                        Example 1:
                        Input: "Translate the text into"
                        Output: " French."

                        Example 2:
                        Input: "Translate the text into "
                        Output: "French."

                        Example 3:
                        Input: "Make the background color of the button"
                        Output: " blue."
                    """
            llm = LlmClient(ModelType.GPT_35_TURBO, system_prompt=system_prompt)

            prompt = f"""
                        Complete the following sentence:
            
                        {prompt}
                    """

            llm_response = llm.get_completions(prompt)

            # Assuming the response is a single completed sentence
            completion = llm_response.strip()

            print(f'Completion: {completion}')
            return jsonify({"suggestion": completion})
        except Exception as e:
            return jsonify({"error": str(e)}), 400


    def run(self, host="0.0.0.0", port=4002):
        self.app.run(host=host, port=port, debug=True)
