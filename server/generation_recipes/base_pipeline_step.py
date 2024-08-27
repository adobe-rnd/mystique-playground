from abc import ABC
from server.generation_recipes.base_recipe import BaseGenerationRecipe
from server.job_manager import JobStatus
from server.pipeline_step import PipelineStep


class BasePipelineStep(PipelineStep, ABC):
    def __init__(self, recipe: BaseGenerationRecipe, **kwargs):
        super().__init__(**kwargs)
        self.recipe = recipe

    def update_status(self, message):
        """
        Helper method to update the job status using the recipe.
        """
        self.recipe.set_status(JobStatus.PROCESSING, message)
