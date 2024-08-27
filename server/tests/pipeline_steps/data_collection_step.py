from typing import List, Dict
from server.pipeline_step import PipelineStep


class DataCollectionStep(PipelineStep):
    def __init__(self, source: str):
        super().__init__(source=source)
        self.source = source

    @staticmethod
    def get_unique_id() -> str:
        return "data_collection_step"

    @staticmethod
    def get_name() -> str:
        return "Data Collection Step"

    @staticmethod
    def get_description() -> str:
        return "This step collects data from the specified source."

    def process(self) -> Dict[str, List[str]]:
        """
        Collect data from the specified source.

        Returns:
            A dictionary with a key 'raw_data' containing a list of collected data points.
        """
        print(f"Collecting data from source: {self.source}")
        # Simulate data collection based on the source
        collected_data = ["data point 1", "data point 2", "data point 3"]
        return {"raw_data": collected_data}
