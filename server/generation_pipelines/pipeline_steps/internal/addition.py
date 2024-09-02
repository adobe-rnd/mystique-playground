from dataclasses import dataclass

from server.pipeline_step import PipelineStep

@dataclass
class ProcessResult:
    result: int

class AdditionStep(PipelineStep):
    def __init__(self, **config):
        super().__init__(**config)

    @staticmethod
    def get_unique_id() -> str:
        return "addition_step"

    @staticmethod
    def get_name() -> str:
        return "Addition"

    @staticmethod
    def get_description() -> str:
        return "Performs addition of two numbers."

    # make the return type of process a dictionary with specific keys
    async def process(self, a: int, b: int) -> ProcessResult:
        return ProcessResult(result=a + b)
