import json
from typing import Dict, Any, Union

from server.pipeline_step import PipelineStep


class NestedPipelineStep(PipelineStep):
    def __init__(self, pipeline: 'Pipeline', definition: Dict[str, Any], **config):
        super().__init__(pipeline, **config)
        self.definition = definition

    @staticmethod
    def get_type() -> str:
        return "pipeline"

    @staticmethod
    def get_name() -> str:
        return "Pipeline"

    @staticmethod
    def get_description() -> str:
        return "A step that runs a nested pipeline."

    async def process(self, **inputs: Any) -> Dict[str, Any]:
        try:
            print(f"Running nested pipeline with inputs: {inputs}")

            # Check if inputs are properly formatted
            if not isinstance(inputs, dict):
                raise ValueError("Inputs must be a dictionary")

            from server.pipeline import Pipeline

            nested_pipeline = Pipeline(
                job_id=self.pipeline.job_id,
                definition=self.definition,
                steps_folder=self.pipeline.steps_folder,
                pipelines_folder=self.pipeline.pipelines_folder,
                initial_params=inputs,  # Use inputs as initial params for the nested pipeline
                pipeline_context=self.pipeline.pipeline_context
            )

            print(f"Initialized nested pipeline: {nested_pipeline}")

            # Run the nested pipeline
            await nested_pipeline.run()

            print(f"Nested pipeline finished running")

            # Collect the outputs from the nested pipeline
            nested_outputs = nested_pipeline.get_output()

            return nested_outputs

        except Exception as e:
            print(f"Failed to run nested pipeline: {e}")
            raise e

    def push_update(self, message: str):
        """Push an update message to the parent pipeline."""
        super().push_update(f"[NestedPipeline] {message}")
