import json
import time

from flask import Flask, jsonify, request, Response, send_from_directory
import os

from flask_cors import CORS

from server.job_manager import JobManager, JobStatus
from server.generation_recipes.standard_generation_recipe import StandardGenerationRecipe
from server.shared.file_utils import handle_file_upload

UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'

class WebCreator:
    def __init__(self):
        self.app = Flask(__name__)
        self.job_manager = JobManager()
        self.register_routes()
        CORS(self.app)

        # Create the uploads and generated folders if they don't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        if not os.path.exists(GENERATED_FOLDER):
            os.makedirs(GENERATED_FOLDER)

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
            user_intent = request.form.get("intent")
            website_url = request.form.get("websiteUrl")
            file_paths = handle_file_upload(request.files, UPLOAD_FOLDER)

            job_id = self.job_manager.generate_job_id()
            job = StandardGenerationRecipe(job_id, file_paths, user_intent, website_url)
            self.job_manager.add_job(job)

            return jsonify({"job_id": job_id}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def job_status_stream(self, job_id):
        job = self.job_manager.get_job_status(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404

        def generate():
            while job.status != JobStatus.COMPLETED:
                if job.updates:
                    update = job.updates.pop(0)
                    yield f"data: {json.dumps(update)}\n\n"
                time.sleep(1)
            yield f"data: {json.dumps({'status': JobStatus.COMPLETED.value})}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    def preview_markup(self, job_id):
        try:
            folder_name = job_id
            file_name = "markup.html"
            folder_path = os.path.join(GENERATED_FOLDER, folder_name)

            if not os.path.exists(os.path.join(folder_path, file_name)):
                return jsonify({"error": "File not found"}), 404

            return send_from_directory(os.path.join('../', folder_path), file_name)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def run(self, host="0.0.0.0", port=4003):
        self.job_manager.start_worker_thread()
        self.app.run(host=host, port=port, debug=True)