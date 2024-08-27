from abc import ABC, abstractmethod
from typing import Dict, Any


class PipelineStep(ABC):
    def __init__(self, **config):
        self.inputs: Dict[str, str] = {}  # Holds input mapping configuration
        self.config = config  # Holds configuration specific to the step

    @staticmethod
    @abstractmethod
    def get_unique_id() -> str:
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
    async def process(self, **kwargs: Any) -> Any:
        """Process the data and return the result."""
        pass
