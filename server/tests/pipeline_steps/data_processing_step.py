from typing import List, Dict
from server.pipeline_step import PipelineStep


class DataProcessingStep(PipelineStep):
    def __init__(self, processing_mode: str):
        super().__init__(processing_mode=processing_mode)
        self.processing_mode = processing_mode

    @staticmethod
    def get_unique_id() -> str:
        return "data_processing_step"

    @staticmethod
    def get_name() -> str:
        return "Data Processing Step"

    @staticmethod
    def get_description() -> str:
        return "This step processes the collected raw data using the specified mode."

    def process(self, raw_data: List[str]) -> Dict[str, str]:
        print(f"Processing data: {raw_data} using mode: {self.processing_mode}")
        # Simulate data processing based on the mode
        summary = f"Processed ({self.processing_mode}): " + ", ".join(raw_data)
        return {"summary": summary}
