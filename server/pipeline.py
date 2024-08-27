import inspect
import os
import importlib.util
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Any, Type, get_type_hints, Union
import json

import asyncio

from server.pipeline_step import PipelineStep


class Pipeline:
    def __init__(self, steps_folder: str, runtime_dependencies: Dict[str, Any] = None):
        self.steps: Dict[str, Type[PipelineStep]] = {}  # Store classes, not instances initially
        self.step_instances: Dict[str, PipelineStep] = {}  # Store step instances once configured
        self.step_dependencies: Dict[str, List[str]] = {}
        self.step_results: Dict[str, Any] = {}
        self.runtime_dependencies = runtime_dependencies or {}  # Store runtime dependencies

        # Automatically discover steps when the pipeline is initialized
        self.discover_steps(steps_folder)

    def discover_steps(self, folder: str):
        """Dynamically discover all pipeline step classes from the specified folder and subfolders."""
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".py"):
                    module_path = os.path.join(root, file)
                    self._load_module_from_path(module_path)

    def _load_module_from_path(self, module_path: str):
        """Load a Python module from a given path and register any PipelineStep classes."""
        module_name = Path(module_path).stem
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type) and issubclass(attribute, PipelineStep) and attribute is not PipelineStep:
                self.steps[attribute.get_unique_id()] = attribute  # Store class type for later instantiation

    def load_pipeline_from_json(self, config: Union[str, Dict[str, Any]]):
        """Load and configure the pipeline from a JSON file or an inline JSON dictionary."""
        if isinstance(config, str):  # Config provided as a file path
            with open(config, 'r') as f:
                config = json.load(f)

        # First, gather all step configurations
        for step_config in config["steps"]:
            step_id = step_config["id"]
            inputs = step_config.get("inputs", {})
            step_instance_config = step_config.get("config", {})  # Step-specific configuration

            # Ensure the step ID exists in the discovered steps
            if step_id in self.steps:
                step_class = self.steps[step_id]
                step_instance = step_class(**step_instance_config, **self.runtime_dependencies)  # Instantiate with step-specific config
                step_instance.inputs = inputs  # Store the input mapping configuration in the step instance
                self.register_step(step_instance)
            else:
                raise ValueError(f"Step ID {step_id} not found in discovered steps.")

        # Now, resolve dependencies based on input mappings
        self._resolve_dependencies()

    def register_step(self, step: PipelineStep):
        """Register a pipeline step."""
        step_id = step.get_unique_id()
        self.step_instances[step_id] = step
        self.step_dependencies[step_id] = []  # Dependencies will be resolved later

    def _resolve_dependencies(self):
        """Automatically determine dependencies based on input references in the configuration."""
        for step_id, step_instance in self.step_instances.items():
            inputs = step_instance.inputs
            dependencies = set()

            for input_name, source in inputs.items():
                if '.' in source:
                    parts = source.split('.')
                    if len(parts) == 2:
                        dependency_id, _ = parts  # Extract the step ID from the input reference
                    else:
                        raise ValueError(f"Invalid input source format '{source}' for step '{step_id}'")
                else:
                    # If no dot is found, assume the entire source is the dependency ID
                    dependency_id = source

                if dependency_id in self.step_instances:
                    dependencies.add(dependency_id)
                else:
                    raise ValueError(f"Invalid input source '{source}' for step '{step_id}'")

            self.step_dependencies[step_id] = list(dependencies)

    def run(self, initial_params: Dict[str, Any]):
        """Execute the pipeline steps considering their dependencies, starting with initial_params."""
        if initial_params is None:
            raise ValueError("Initial parameters must be provided to run the pipeline.")

        completed_steps = set()

        # Identify all steps without dependencies
        initial_steps = self._get_initial_steps()

        with ThreadPoolExecutor() as executor:
            futures = {}
            # Start all initial steps with the initial_params
            for step_id in initial_steps:
                futures[step_id] = executor.submit(self.run_step, step_id, initial_params)

            while len(completed_steps) < len(self.step_instances):
                # Identify steps that are ready to run (all dependencies are met)
                ready_to_run = [
                    step_id for step_id, deps in self.step_dependencies.items()
                    if step_id not in completed_steps and all(dep in completed_steps for dep in deps)
                ]

                for step_id in ready_to_run:
                    if step_id not in futures:
                        futures[step_id] = executor.submit(self.run_step, step_id, None)

                # Collect results as they complete, handling exceptions if they occur
                for future in as_completed(futures.values()):
                    step_id = [k for k, v in futures.items() if v == future][0]

                    try:
                        # This will re-raise any exceptions that occurred in the step
                        future.result()
                    except Exception as e:
                        # Handle the exception or rethrow it
                        print(f"Exception occurred in step '{step_id}': {e}")
                        # Optionally, clean up or terminate remaining steps here
                        raise e  # Re-raise the exception to be handled by the caller

                    completed_steps.add(step_id)
                    futures.pop(step_id)  # Remove from the list of running futures

    def run_step(self, step_id: str, initial_params: Dict[str, Any] = None):
        step = self.step_instances[step_id]
        input_data = initial_params if initial_params is not None else self.prepare_input_for_step(step)

        self.validate_inputs(step, input_data)

        print(f"Running step: {step.get_name()}")

        if inspect.iscoroutinefunction(step.process):
            result = asyncio.run(step.process(**input_data))
        else:
            result = step.process(**input_data)

        self.step_results[step_id] = result

    def validate_inputs(self, step: PipelineStep, input_data: Dict[str, Any]):
        """Validate that all required inputs for the step are provided, ignoring *args and **kwargs."""
        required_inputs = self.get_step_input_types(step.__class__).keys()

        # Exclude *args and **kwargs from required inputs
        filtered_required_inputs = [
            input_name for input_name in required_inputs
            if input_name not in ('args', 'kwargs')
        ]

        missing_inputs = [
            input_name for input_name in filtered_required_inputs
            if input_name not in input_data
        ]

        if missing_inputs:
            raise ValueError(
                f"Missing required inputs for step '{step.get_name()}': {', '.join(missing_inputs)}"
            )

    def prepare_input_for_step(self, step: PipelineStep) -> Dict[str, Any]:
        """Prepare the input for a step based on its dependencies and expected input type."""
        step_id = step.get_unique_id()
        inputs = {}

        # Map the outputs from dependencies to the named inputs
        for input_name, source in step.inputs.items():
            if '.' in source:
                dependency_id, field_name = source.split('.')
                result = self.step_results[dependency_id]

                # Handle both dict and object outputs
                if isinstance(result, dict):
                    inputs[input_name] = result.get(field_name)
                else:
                    inputs[input_name] = getattr(result, field_name, None)
            else:
                # If the source is a single step ID, use the entire output of that step directly
                dependency_id = source
                result = self.step_results[dependency_id]
                inputs[input_name] = result

        return inputs  # Return a dictionary of named arguments

    def _get_initial_steps(self) -> List[str]:
        """Find all steps that have no dependencies."""
        return [step_id for step_id, deps in self.step_dependencies.items() if not deps]

    def get_step_result(self, step_id: str) -> Any:
        """Retrieve the result of a given step."""
        return self.step_results.get(step_id)

    def get_step_input_types(self, step_class: Type[PipelineStep]) -> Dict[str, Type]:
        """Get the input types expected by the process method of a step."""
        # Use get_type_hints to introspect parameter types of the process method
        type_hints = get_type_hints(step_class.process)
        # Exclude 'self' from the input types
        return {k: v for k, v in type_hints.items() if k != 'self' and k != 'return'}

    def get_step_output_type(self, step_class: Type[PipelineStep]) -> Type:
        """Get the output type of the process method of a step."""
        # Use get_type_hints to introspect the return type of the process method
        type_hints = get_type_hints(step_class.process)
        return type_hints.get('return', Any)
