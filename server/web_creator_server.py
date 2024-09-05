import faulthandler
import json
import signal
import threading
import time

from flask import Flask, jsonify, request, Response, Blueprint, send_from_directory
import os

from flask_cors import CORS

from server.job_manager import JobManager, JobStatus
from server.pipeline import Pipeline
from server.pipeline_metadata_extractor import PipelineStepsMetadataExtractor
from server.shared.file_utils import handle_file_upload

PIPELINE_FOLDER_PATH = "server/generation_pipelines/pipelines"
PIPELINE_STEP_FOLDER_PATH = "server/generation_pipelines/pipeline_steps"

UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'


def load_pipelines_from_folder(folder_path):
    pipelines = {}
    for root, _, files in os.walk(folder_path):  # Use os.walk to traverse all subdirectories
        for filename in files:
            if filename.endswith(".json"):
                with open(os.path.join(root, filename)) as f:
                    config = json.load(f)
                    pipeline_id = config["id"]
                    print(f"Loading pipeline: {pipeline_id} from {os.path.join(root, filename)}")
                    pipelines[pipeline_id] = {
                        "name": config["name"],
                        "description": config["description"],
                        "config": config
                    }
    return pipelines


class WebCreator:
    def __init__(self):
        self.app = Flask(__name__, static_folder='./generation_pipelines/components', static_url_path='/static')
        self.app.register_blueprint(Blueprint('generated', __name__, static_folder='../generated'))
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
        self.app.add_url_rule('/pipelines', view_func=self.get_pipelines, methods=['GET'])
        self.app.add_url_rule('/pipeline/<pipeline_id>', view_func=self.get_pipeline_by_id, methods=['GET'])
        self.app.add_url_rule('/pipeline-steps', view_func=self.get_pipeline_steps, methods=['GET'])
        self.app.add_url_rule('/generated', view_func=self.get_generated_pages, methods=['GET'])
        self.app.add_url_rule('/delete-generated/<job_id>', view_func=self.delete_generated_page, methods=['DELETE'])
        self.app.add_url_rule('/preview/<job_id>', view_func=self.preview_markup, methods=['GET'])

    @staticmethod
    def ok():
        try:
            print("ok")
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def create_pipeline(self, pipeline_id, job_id, job_folder, initial_params):
        print(f"Creating pipeline: {pipeline_id}")
        pipelines = load_pipelines_from_folder(PIPELINE_FOLDER_PATH)
        pipeline = pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")

        config = pipeline.get('config')
        print(f"Pipeline config: {config}")

        print(f"Initial params: {initial_params}")

        pipeline_context={
            'job_id': job_id,
            'job_folder': job_folder,
        }
        print(f"Pipeline context: {pipeline_context}")

        pipeline = Pipeline(
            job_id=job_id,
            definition=config,
            steps_folder=PIPELINE_STEP_FOLDER_PATH,
            pipelines_folder=PIPELINE_FOLDER_PATH,
            initial_params=initial_params,
            pipeline_context=pipeline_context
        )

        print(f"Pipeline created: {pipeline}")

        return pipeline

    def generate(self):
        try:
            # Extract pipeline ID
            pipeline_id = request.form.get("pipelineId")
            print(f"Pipeline ID: {pipeline_id}")

            # print all parameters
            print(f"Request form: {request.form}")
            print(f"Request files: {request.files}")

            # Extract all other dynamic parameters
            dynamic_params = {}
            for key in request.form.keys():
                if key not in ['pipelineId']:
                    dynamic_params[key] = request.form.get(key)

            # first check if there are any files in the request
            for key in request.files:
                # handle file upload
                files = handle_file_upload(request.files.getlist(key), UPLOAD_FOLDER)
                # add the file paths to the dynamic params
                dynamic_params[key] = files

            print(f"Pipeline ID: {pipeline_id}")
            print(f"Dynamic Params: {dynamic_params}")

            # Create a job ID
            job_id = self.job_manager.generate_job_id()
            print(f"Job ID: {job_id}")

            # Create a folder for the job
            job_folder = os.path.join(GENERATED_FOLDER, job_id)
            os.makedirs(job_folder, exist_ok=True)
            print(f"Job folder created: {job_folder}")

            # Create pipeline with the dynamic parameters
            job = self.create_pipeline(pipeline_id, job_id, job_folder, dynamic_params)

            print(f"Adding job to manager: {job}")

            self.job_manager.add_job(job)

            return jsonify({"job_id": job_id}), 200
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400

    def job_status_stream(self, job_id):
        job = self.job_manager.get_job_status(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404

        def generate():
            while True:
                job = self.job_manager.get_job_status(job_id)  # Refresh job status every loop
                updates = []

                # Collect all new updates
                while job.updates:
                    update = job.updates.pop(0)
                    updates.append(update)

                if updates:
                    # Send the status along with the new updates as an array
                    data = {
                        "status": job.status.value,
                        "updates": updates
                    }
                    # If the job is completed, send the result as well
                    if job.status == JobStatus.COMPLETED:
                        result = job.result
                        print(f"Job result: {result}")
                        if 'url' in job.result:
                            url = job.result.get('url')
                            print(f"Sending URL: {url}")
                            data["result"] = url
                            data["result_type"] = "url"
                        else:
                            print(f"Sending result: {result}")
                            data["result"] = job.result
                            data["result_type"] = "json"
                    print(f"Sending new updates: {data}")
                    yield f"data: {json.dumps(data)}\n\n"

                # Break the loop if the job is completed or errored
                if job.status in [JobStatus.COMPLETED, JobStatus.ERROR]:
                    time.sleep(1)
                    break

                time.sleep(0.3)  # Adjust sleep time as necessary

        return Response(generate(), mimetype='text/event-stream')

    def get_pipeline_steps(self):
        try:
            pipeline_metadata_extractor = PipelineStepsMetadataExtractor(PIPELINE_STEP_FOLDER_PATH, PIPELINE_FOLDER_PATH)
            steps = pipeline_metadata_extractor.extract_pipeline_steps()
            print(f"Detected pipeline steps: {steps}")
            return jsonify(steps)
        except Exception as e:
            print(f"Error extracting pipeline steps: {e}")
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_pipelines():
        try:
            pipelines = load_pipelines_from_folder(PIPELINE_FOLDER_PATH)
            print(f"Loaded pipelines: {pipelines}")
            return jsonify([pipeline.get('config') for pipeline in pipelines.values()])
        except Exception as e:
            print(f"Error loading pipelines: {e}")
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_pipeline_by_id(pipeline_id):
        pipeline = load_pipelines_from_folder(PIPELINE_FOLDER_PATH).get(pipeline_id)
        if not pipeline:
            return jsonify({"error": "Pipeline not found"}), 404
        config = pipeline.get('config')
        print(f"Pipeline config: {config}")
        return jsonify(config)

    @staticmethod
    def get_generated_pages():
        return jsonify([
            f for f in os.listdir(GENERATED_FOLDER)
            if os.path.isdir(os.path.join(GENERATED_FOLDER, f)) and
               os.path.isfile(os.path.join(GENERATED_FOLDER, f, 'index.html'))
        ])

    @staticmethod
    def delete_generated_page(job_id):
        try:
            folder_name = job_id
            folder_path = os.path.join(GENERATED_FOLDER, folder_name)

            if not os.path.exists(folder_path):
                return jsonify({"error": "Folder not found"}), 404

            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            os.rmdir(folder_path)
            return jsonify({"message": "Folder deleted"}), 200
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400

    @staticmethod
    def preview_markup(job_id):
        try:
            folder_name = job_id
            file_name = "index.html"
            folder_path = os.path.join(GENERATED_FOLDER, folder_name)

            if not os.path.exists(os.path.join(folder_path, file_name)):
                return jsonify({"error": "File not found"}), 404

            return send_from_directory(os.path.join('../', folder_path), file_name)
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400

    def run(self, host="0.0.0.0", port=4003):
        self.job_manager.start_worker_thread()
        self.app.run(host=host, port=port, debug=True)
