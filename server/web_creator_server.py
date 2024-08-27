import faulthandler
import json
import signal
import threading
import time
import importlib.util

from flask import Flask, jsonify, request, Response, Blueprint, send_from_directory
import os

from flask_cors import CORS

from server.generation_recipes.base_recipe import BaseGenerationRecipe
from server.job_manager import JobManager, JobStatus
from server.pipeline_metadata_extractor import PipelineMetadataExtractor
from server.shared.file_utils import handle_file_upload

RECIPE_FOLDER_PATH = "server/generation_recipes"
PIPELINE_FOLDER_PATH = "server/generation_recipes/pipelines"
PIPELINE_STEP_FOLDER_PATH = "server/generation_recipes/pipeline_steps"

UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'


def load_generation_recipes_from_folder(folder_path):
    recipes = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module_path = os.path.join(folder_path, filename)

            # Dynamically load the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find all subclasses of BaseGenerationRecipe in the module
            for obj in module.__dict__.values():
                if isinstance(obj, type) and issubclass(obj, BaseGenerationRecipe) and obj is not BaseGenerationRecipe:
                    recipe_id = obj.get_id()
                    print(f"Loading recipe: {recipe_id}")
                    recipes[recipe_id] = {
                        "name": obj.name(),
                        "description": obj.description(),
                        "class": obj
                    }
    return recipes


class WebCreator:
    def __init__(self):
        self.app = Flask(__name__, static_folder='./generation_recipes/components', static_url_path='/static')
        self.app.register_blueprint(Blueprint('generated', __name__, static_folder='../generated'))
        self.job_manager = JobManager()
        self.register_routes()
        self.recipes = load_generation_recipes_from_folder(RECIPE_FOLDER_PATH)
        self.pipeline_metadata_extractor = PipelineMetadataExtractor(PIPELINE_STEP_FOLDER_PATH)

        print(self.recipes)

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
        self.app.add_url_rule('/recipes', view_func=self.get_generation_recipes, methods=['GET'])
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

    def generate(self):
        try:
            user_intent = request.form.get("intent")
            website_url = request.form.get("websiteUrl")
            recipe = request.form.get("recipe")
            print(user_intent, website_url, recipe)
            file_paths = handle_file_upload(request.files, UPLOAD_FOLDER)

            job_id = self.job_manager.generate_job_id()
            print(f"Job ID: {job_id}")

            # Create a folder for the job
            job_folder = os.path.join(GENERATED_FOLDER, job_id)
            os.makedirs(job_folder, exist_ok=True)
            print(f"Job folder created: {job_folder}")

            # instantiate the class based on the recipe or return error if recipe not found
            job_class = self.recipes.get(recipe)
            if not job_class:
                return jsonify({"error": "Recipe not found"}), 400

            job = job_class["class"](job_id, job_folder, file_paths, user_intent, website_url)

            self.job_manager.add_job(job)

            return jsonify({"job_id": job_id}), 200
        except Exception as e:
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
                    print(f"Sending new updates: {data}")
                    yield f"data: {json.dumps(data)}\n\n"

                # Break the loop if the job is completed or errored
                if job.status in [JobStatus.COMPLETED, JobStatus.ERROR]:
                    time.sleep(1)
                    break

                time.sleep(0.3)  # Adjust sleep time as necessary

        return Response(generate(), mimetype='text/event-stream')

    def get_generation_recipes(self):
        print("get_generation_recipes")
        print(self.recipes)
        return jsonify([{"id": key, "name": value["name"], "description": value["description"]} for key, value in self.recipes.items()])

    def get_pipeline_steps(self):
        return jsonify([step for step in self.pipeline_metadata_extractor.extract_pipeline_steps()])

    @staticmethod
    def get_pipelines():
        pipelines = []
        for filename in os.listdir(PIPELINE_FOLDER_PATH):
            if filename.endswith(".json"):
                with open(os.path.join(PIPELINE_FOLDER_PATH, filename)) as f:
                    pipeline = json.load(f)
                    pipelines.append(pipeline)
        return jsonify(pipelines)

    @staticmethod
    def get_pipeline_by_id(pipeline_id):
        pipeline_path = os.path.join(PIPELINE_FOLDER_PATH, f"{pipeline_id}.json")
        if not os.path.exists(pipeline_path):
            return jsonify({"error": "Pipeline not found"}), 404
        with open(pipeline_path) as f:
            pipeline = json.load(f)
        return jsonify(pipeline)

    @staticmethod
    def get_generated_pages():
        return jsonify([f for f in os.listdir(GENERATED_FOLDER) if os.path.isdir(os.path.join(GENERATED_FOLDER, f))])

    @staticmethod
    def delete_generated_page(job_id):
        # also take care of deleting the folder if it is not empty
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
