from typing import Any

from server.pipeline_step import PipelineStep


class DivisionStep(PipelineStep):
    def __init__(self, runs=1, **config):
        super().__init__(**config)
        self.run_count = runs
        print(f'DivisionStep: __init__ with runs={runs}')

    @staticmethod
    def get_unique_id() -> str:
        return "division_step"

    @staticmethod
    def get_name() -> str:
        return "Division Step"

    @staticmethod
    def get_description() -> str:
        return "Performs division of two numbers."

    async def process(self, a: int, b: int) -> dict:
        self.run_count += 1
        if b != 0:
            return { "result": a / b }
        else:
            raise ValueError("Division by zero")

