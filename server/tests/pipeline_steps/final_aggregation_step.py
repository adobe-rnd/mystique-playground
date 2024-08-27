from typing import Dict
from server.pipeline_step import PipelineStep


class FinalAggregationStep(PipelineStep):
    def __init__(self, aggregation_strategy: str):
        super().__init__(aggregation_strategy=aggregation_strategy)
        self.aggregation_strategy = aggregation_strategy

    @staticmethod
    def get_unique_id() -> str:
        return "final_aggregation_step"

    @staticmethod
    def get_name() -> str:
        return "Final Aggregation Step"

    @staticmethod
    def get_description() -> str:
        return "This step aggregates summaries using the specified strategy."

    def process(self, summary: str) -> Dict[str, str]:
        print(f"Aggregating results using strategy: {self.aggregation_strategy}")
        # Simulate aggregation based on the strategy
        final_report = f"Final Report (Strategy: {self.aggregation_strategy}):\n{summary}"
        return {"final_report": final_report}
