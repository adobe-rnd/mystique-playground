import base64
import random
import string
import json
import os
import time
from datetime import datetime
from typing import List
from flask import Flask, Response, request, jsonify, make_response, send_from_directory, flash, send_file
from flask_cors import CORS
import mammoth
import threading
import queue
import traceback
import asyncio
import signal
import sys

from server.file_utils import handle_file_upload
from server.llm import LlmClient, ModelType, parse_markdown_output
from server.scraper import WebScraper

from server.component_templates import html_structure, css_variables, generate_css

from enum import Enum

class JobStatus(Enum):
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    ERROR = 'error'

UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'

class Doc2Web:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        self.register_routes()
        CORS(self.app)

        # Create the uploads and generated folders if they don't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        if not os.path.exists(GENERATED_FOLDER):
            os.makedirs(GENERATED_FOLDER)

        self.job_queue = queue.Queue()
        self.job_status = {}
        self.worker_thread = None

    def register_routes(self):
        self.app.add_url_rule('/ok', view_func=self.ok, methods=['GET'])
        self.app.add_url_rule('/generate', view_func=self.generate, methods=['POST'])
        self.app.add_url_rule('/status/<job_id>', view_func=self.job_status_stream, methods=['GET'])
        self.app.add_url_rule('/preview/<job_id>', view_func=self.preview_markup, methods=['GET'])

    @staticmethod
    def ok():
        try:
            print("ok")
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def generate(self):
        try:
            # Extract user intent from the request
            user_intent = request.form.get("intent")
            print("User intent:", user_intent)

            website_url = request.form.get("websiteUrl")
            print("Website URL:", website_url)

            # Handle file upload
            file_paths = handle_file_upload(request.files, UPLOAD_FOLDER)
            print('Uploaded files:', file_paths)

            # Create a unique job ID
            job_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            self.job_status[job_id] = {'status': JobStatus.QUEUED, 'updates': [{"message": "Job queued. Processing will start soon..."}]}

            # Schedule the job to be processed asynchronously
            self.job_queue.put((job_id, file_paths, user_intent, website_url))

            return jsonify({"job_id": job_id}), 200
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400

    def job_status_stream(self, job_id):
        def generate():
            print(f"Starting job status stream for job ID: {self.job_status[job_id]['status']}")
            while self.job_status[job_id]['status'] != JobStatus.COMPLETED:
                if self.job_status[job_id]['updates']:
                    update = self.job_status[job_id]['updates'].pop(0)
                    yield f"data: {json.dumps(update)}\n\n"
                time.sleep(1)
            yield f"data: {json.dumps({'status': JobStatus.COMPLETED.value})}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    def start_worker_thread(self):
        self.worker_thread = threading.Thread(target=self.start_worker_loop, daemon=True)
        self.worker_thread.start()

    def start_worker_loop(self):
        asyncio.run(self.worker_loop())

    async def worker_loop(self):
        while True:
            job_id, file_paths, user_intent, website_url = await asyncio.to_thread(self.job_queue.get)
            self.set_job_status(job_id, JobStatus.PROCESSING, 'Job processing started')
            try:
                await self.process_job(job_id, file_paths, user_intent, website_url)
            except Exception as e:
                self.set_job_status(job_id, JobStatus.ERROR, error=str(e))
                print(e)
                print(traceback.format_exc())
            self.job_queue.task_done()

    async def process_job(self, job_id, file_paths, user_intent, website_url):
        try:
            self.set_job_status(job_id, JobStatus.PROCESSING, 'Reading uploaded files...')

            markdown_contents = []
            for file_path in file_paths:
                with open(file_path, "rb") as docx_file:
                    result = mammoth.convert_to_markdown(docx_file)
                    markdown_content = result.value
                    markdown_contents.append(markdown_content)

                os.remove(file_path)

            self.set_job_status(job_id, JobStatus.PROCESSING, 'Generating page structure...')
            page_content = self.create_page_structure(markdown_contents, user_intent)
            self.set_job_status(job_id, JobStatus.PROCESSING, 'Page structure generated.')

            self.set_job_status(job_id, JobStatus.PROCESSING, 'Capturing screenshot of the website...')
            scraper = WebScraper()
            html, screenshot = await scraper.get_html_and_screenshot(website_url, selector='body', with_styles=False)
            self.set_job_status(job_id, JobStatus.PROCESSING, 'Screenshot captured.')

            self.set_job_status(job_id, JobStatus.PROCESSING, 'Inferring CSS variables...')
            inferred_values = self.infer_css_values(screenshot)
            inferred_css = generate_css(inferred_values)
            self.set_job_status(job_id, JobStatus.PROCESSING, 'CSS variables inferred.')

            self.set_job_status(job_id, JobStatus.PROCESSING, 'Generating HTML layout...')
            html_output = self.generate_html_layout(page_content, inferred_css, user_intent)
            self.set_job_status(job_id, JobStatus.PROCESSING, 'HTML layout generated.')

            folder_name = job_id
            folder_path = os.path.join(GENERATED_FOLDER, folder_name)
            os.makedirs(folder_path)

            file_name = "markup.html"
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "w") as file:
                file.write(html_output)

            self.set_job_status(job_id, JobStatus.COMPLETED, 'File saved', folder=folder_name, file=file_name)
        except Exception as e:
            self.set_job_status(job_id, JobStatus.ERROR, error=str(e))

    def set_job_status(self, job_id, status, message=None, **kwargs):
        if job_id not in self.job_status:
            return

        self.job_status[job_id]['status'] = status
        if message:
            update = {'message': message}
            update.update(kwargs)
            self.job_status[job_id]['updates'].append(update)

    def create_page_structure(self, markdown_contents: List[str], user_intent: str):
        system_prompt = '''
        '''
        client = LlmClient(model=ModelType.GPT_4_OMNI, system_prompt=system_prompt)

        prompt = f'''
        You are an experienced web developer with a strong background in content management and page structuring. 
        Your task is to merge markdown content from multiple sources into a cohesive and well-organized markdown document.
        
        Below is the markdown content extracted from various documents:
    
        {"\n\n".join(markdown_contents)}
    
        The goal is to combine this content into a single, logically structured markdown page that aligns with the following user intent:
    
        User Intent: {user_intent}
    
        Please ensure that the final document:
        - Maintains a clear and logical flow
        - Uses appropriate markdown headings to organize sections
        - Ensures consistency in formatting and style
        - Includes any necessary transitions to connect disparate sections smoothly
        - Preserves the original meaning and intent of each section
    
        Begin your response with the merged and structured markdown content:
        '''
        llm_response = client.get_completions(prompt, temperature=0.0)

        return parse_markdown_output(llm_response, lang='markdown')

    def infer_css_values(self, screenshot: bytes) -> dict:
        infer_values_prompt = f"""
            You are a professional web developer tasked with inferring the CSS variables from a provided screenshot.
            Extract the primary colors, font family, font size, and dimensions such as header height, footer height, sidebar width, padding, and margin.
            Use the extracted values to populate the following variables:
            
            {', '.join(css_variables.keys())}
            
            Return the values in a JSON format. Here is an example format for the JSON response:
            
            {json.dumps(css_variables, indent=4)}
            
            Provide the JSON response with the inferred values.
        """
        print(infer_values_prompt)
        client = LlmClient(model=ModelType.GPT_4_OMNI)
        inferred_values_response = client.get_completions(infer_values_prompt, temperature=0.0, image_list=[screenshot])
        print(inferred_values_response)

        return json.loads(parse_markdown_output(inferred_values_response, lang='json'))

    def generate_html_layout(self, markdown_content: str, inferred_css: str, user_intent: str) -> str:
        full_prompt = f'''
        You are a professional web developer tasked with transforming markdown content into a well-structured HTML page layout.
        The page must be composed only of the components defined in the given HTML structure and styled using the provided CSS.
        
        Ensure the layout aligns with the user's intent: {user_intent}.
        
        Convert the following markdown content into a well-structured HTML page layout with the given styles.
    
        CSS:
        ```
        {inferred_css}
        ```
    
        HTML Fragments to Use:
        ```
        {html_structure}
        ```
    
        Markdown Content:
        ```
        {markdown_content}
        ```
        '''
        print(full_prompt)
        client = LlmClient(model=ModelType.GPT_4_OMNI)
        llm_response = client.get_completions(full_prompt, temperature=0.0)
        print(llm_response)

        return parse_markdown_output(llm_response, lang='html')

    def preview_markup(self, job_id):
        try:
            # Fetch folder name from job status updates
            folder_name = job_id
            file_name = "markup.html"

            folder_path = os.path.join(GENERATED_FOLDER, folder_name)

            if not os.path.exists(os.path.join(folder_path, file_name)):
                return jsonify({"error": "File not found"}), 404

            return send_from_directory(os.path.join('../', folder_path), file_name)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def run(self, host="0.0.0.0", port=4003):
        self.start_worker_thread()
        self.app.run(host=host, port=port, debug=True)
