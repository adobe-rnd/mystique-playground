from abc import ABC, abstractmethod
from typing import Dict, Any, TypeVar, Union

T = TypeVar('T')
StepResultDict = Dict[str, T]


class PipelineStep(ABC):
    def __init__(self, pipeline: 'Pipeline', **config):
        self.pipeline = pipeline
        self.config = config
        self.inputs: Dict[str, str] = {}

    @staticmethod
    @abstractmethod
    def get_type() -> str:
        """Return a unique identifier for the step."""
        pass

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Return a human-readable name for the step."""
        pass

    @staticmethod
    @abstractmethod
    def get_description() -> str:
        """Return a human-readable description for the step."""
        pass

    @abstractmethod
    async def process(self, **inputs: Any) -> Any:
        """Process the data asynchronously and return the result."""
        pass

    def push_update(self, message: str):
        """Push an update message to the pipeline."""
        self.pipeline.push_update(message)
