from server.pipeline_step import PipelineStep


class AdditionStep(PipelineStep):
    def __init__(self, **config):
        super().__init__(**config)

    @staticmethod
    def get_unique_id() -> str:
        return "addition_step"

    @staticmethod
    def get_name() -> str:
        return "Addition Step"

    @staticmethod
    def get_description() -> str:
        return "Performs addition of two numbers."

    async def process(self, a: int, b: int) -> dict:
        return { "result": a + b }
