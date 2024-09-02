from server.pipeline_step import PipelineStep


class MultiplicationStep(PipelineStep):
    @staticmethod
    def get_unique_id() -> str:
        return "multiplication_step"

    @staticmethod
    def get_name() -> str:
        return "Multiplication Step"

    @staticmethod
    def get_description() -> str:
        return "Performs multiplication of two numbers."

    async def process(self, a: int, b: int) -> dict:
        return { "result": a * b }
