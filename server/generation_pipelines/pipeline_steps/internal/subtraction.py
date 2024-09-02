from dataclasses import dataclass

from server.pipeline_step import PipelineStep

@dataclass
class ProcessResult:
    result: int

class SubtractionStep(PipelineStep):
    @staticmethod
    def get_unique_id() -> str:
        return "subtraction_step"

    @staticmethod
    def get_name() -> str:
        return "Subtraction"

    @staticmethod
    def get_description() -> str:
        return "Performs subtraction of two numbers."

    async def process(self, a: int, b: int) -> ProcessResult:
        return ProcessResult(result=a - b)
