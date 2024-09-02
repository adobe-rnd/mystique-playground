from server.pipeline_step import PipelineStep


class SubtractionStep(PipelineStep):
    @staticmethod
    def get_unique_id() -> str:
        return "subtraction_step"

    @staticmethod
    def get_name() -> str:
        return "Subtraction Step"

    @staticmethod
    def get_description() -> str:
        return "Performs subtraction of two numbers."

    async def process(self, a: int, b: int) -> dict:
        return { "result": a - b }
