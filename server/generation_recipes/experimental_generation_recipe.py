from server.generation_recipes.base_recipe import BaseGenerationRecipe
from server.job_manager import JobStatus, Job
from server.pipeline import Pipeline


class ExperimentalGenerationRecipe(BaseGenerationRecipe):
    def __init__(self, job_id, job_folder, uploaded_files, user_intent, website_url):
        super().__init__(job_id)
        self.job_folder = job_folder
        self.uploaded_files = uploaded_files
        self.user_intent = user_intent
        self.website_url = website_url

    @staticmethod
    def get_id():
        return 'experimental_generation_recipe'

    @staticmethod
    def name():
        return 'Pipeline Test (New)'

    @staticmethod
    def description():
        return 'A test pipeline for generating a web page.'

    async def run(self):
        self.set_status(JobStatus.PROCESSING, 'Creating pipeline...')

        pipeline = Pipeline('server/generation_recipes/pipeline_steps', runtime_dependencies={
            'recipe': self,
            'job_id': self.job_id,
            'job_folder': self.job_folder,
        })

        self.set_status(JobStatus.PROCESSING, 'Loading pipeline steps...')
        pipeline.load_pipeline_from_json('server/generation_recipes/pipelines/experimental_pipeline.json')

        self.set_status(JobStatus.PROCESSING, 'Running pipeline...')
        pipeline.run(initial_params={
            'uploaded_files': self.uploaded_files,
            'user_intent': self.user_intent,
            'website_url': self.website_url
        })
        self.set_status(JobStatus.PROCESSING, 'Pipeline completed.')
