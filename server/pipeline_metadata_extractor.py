import importlib.util

from server.pipeline_step import PipelineStep


import os
import importlib.util
import inspect
import json
from abc import ABC
from dataclasses import is_dataclass, fields


class PipelineMetadataExtractor:
    def __init__(self, root_folder: str):
        self.root_folder = root_folder

    def extract_pipeline_steps(self):
        pipeline_steps = []
        for dirpath, _, filenames in os.walk(self.root_folder):
            for filename in filenames:
                if filename.endswith(".py"):
                    module_path = os.path.join(dirpath, filename)
                    module_name = self._get_module_name_from_path(module_path)
                    pipeline_steps.extend(self._extract_from_module(module_path, module_name))
        return pipeline_steps

    def _get_module_name_from_path(self, module_path: str) -> str:
        """Generates a module name based on the file path."""
        return module_path.replace(os.sep, ".").rstrip(".py")

    def _extract_from_module(self, module_path: str, module_name: str):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        pipeline_steps = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if self._is_pipeline_step(obj):
                pipeline_steps.append(self._extract_metadata(obj))
        return pipeline_steps

    def _is_pipeline_step(self, cls) -> bool:
        """Checks if the class inherits from PipelineStep, isn't abstract, and isn't PipelineStep itself."""
        return issubclass(cls, PipelineStep) and cls is not PipelineStep and not inspect.isabstract(cls)

    def _extract_metadata(self, cls):
        metadata = {
            "id": self._safe_call(cls, "get_unique_id"),
            "name": self._safe_call(cls, "get_name"),
            "description": self._safe_call(cls, "get_description"),
            "inputs": [],
            "outputs": []
        }

        process_method = getattr(cls, "process", None)
        if process_method:
            metadata["inputs"] = self._get_filtered_inputs(process_method)
            metadata["outputs"] = self._infer_outputs(process_method)

        return metadata

    def _safe_call(self, cls, method_name):
        """Safely calls a static method and returns the result, or None if the method isn't defined."""
        method = getattr(cls, method_name, None)
        if method and inspect.isfunction(method):
            try:
                return method()
            except Exception:
                return None
        return None

    def _get_filtered_inputs(self, method):
        """Filters out 'self', 'args', and 'kwargs' from the method signature."""
        inputs = [
            param.name
            for param in inspect.signature(method).parameters.values()
            if param.name not in ["self", "args", "kwargs"]
        ]
        return inputs

    def _infer_outputs(self, method):
        """Attempts to infer outputs by inspecting the return type annotation."""
        return_annotation = inspect.signature(method).return_annotation
        if inspect.isclass(return_annotation) and is_dataclass(return_annotation):
            # If the return annotation is a dataclass, extract its field names
            return [field.name for field in fields(return_annotation)]
        else:
            # Otherwise, return None since it's not a dataclass
            return None


def extract_pipeline_metadata(root_folder: str) -> str:
    extractor = PipelineMetadataExtractor(root_folder)
    pipeline_steps = extractor.extract_pipeline_steps()
    return json.dumps(pipeline_steps, indent=4)

# Example usage
if __name__ == "__main__":
    root_folder = "server/generation_recipes/pipeline_steps"
    print(extract_pipeline_metadata(root_folder))
