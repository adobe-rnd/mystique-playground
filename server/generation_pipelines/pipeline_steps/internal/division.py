from dataclasses import dataclass

from server.pipeline_step import PipelineStep

@dataclass
class ProcessResult:
    result: int

class DivisionStep(PipelineStep):
    def __init__(self, **config):
        super().__init__(**config)

    @staticmethod
    def get_type() -> str:
        return "division_step"

    @staticmethod
    def get_name() -> str:
        return "Division"

    @staticmethod
    def get_description() -> str:
        return "Performs division of two numbers."

    async def process(self, a: int, b: int) -> ProcessResult:
        if b != 0:
            return ProcessResult(result=a // b)
        else:
            raise ValueError("Division by zero")

