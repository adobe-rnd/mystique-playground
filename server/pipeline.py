import inspect
import os
import importlib.util
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Any, Type, get_type_hints, Union
import asyncio

from server.job_manager import Job
from server.pipeline_step import PipelineStep


class Pipeline(Job):
    def __init__(self, job_id: str, config: Union[str, Dict[str, Any]], steps_folder: str, initial_params: Dict[str, Any], pipeline_context: Dict[str, Any] = None):
        super().__init__(job_id=job_id)  # Initialize BaseGenerationRecipe with a unique job_id
        self.steps: Dict[str, Type[PipelineStep]] = {}  # Store classes, not instances initially
        self.step_instances: Dict[str, PipelineStep] = {}  # Store step instances once configured
        self.step_dependencies: Dict[str, List[str]] = {}
        self.step_results: Dict[str, Any] = {}
        self.pipeline_context = pipeline_context or {}  # Store pipeline context
        self.global_inputs: Dict[str, Any] = {}  # Store global inputs from the pipeline config
        self.initial_params = initial_params  # Store initial parameters

        # Automatically discover steps when the pipeline is initialized
        self.discover_steps(steps_folder)

        # Load pipeline configuration from JSON
        self.create_pipeline_from_json(config)

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

    def create_pipeline_from_json(self, config: Union[str, Dict[str, Any]]):
        # Store global inputs for validation
        self.global_inputs = {input_name: None for input_name in config.get("inputs", [])}

        # First, gather all step configurations
        for step_config in config["steps"]:
            step_id = step_config.get("id")
            inputs = step_config.get("inputs", {})
            step_instance_config = step_config.get("config", {})  # Step-specific configuration

            # Validate that all input references contain a dot and are valid
            self.validate_input_references(inputs, step_id)

            # Ensure the step ID exists in the discovered steps
            if step_id in self.steps:
                step_class = self.steps[step_id]
                step_instance = step_class(pipeline=self, **step_instance_config, **self.pipeline_context)  # Instantiate with step-specific config
                step_instance.inputs = inputs  # Store the input mapping configuration in the step instance
                self.register_step(step_instance)
            else:
                raise ValueError(f"Step ID {step_id} not found in discovered steps.")

        # Now, resolve dependencies based on input mappings
        self._resolve_dependencies()

        # Store output mapping from the config
        self.output_mapping = config.get("outputs", {})

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
                        dependency_id, _ = parts  # Extract the step ID or 'inputs' from the input reference
                    else:
                        raise ValueError(f"Invalid input source format '{source}' for step '{step_id}'")
                else:
                    raise ValueError(f"Invalid input source '{source}' for step '{step_id}' - must contain a dot")

                # Check if source is a global input or a valid step
                if dependency_id == 'inputs':  # Treat global inputs as dependencies on 'inputs'
                    dependencies.add('inputs')
                elif dependency_id in self.step_instances:  # Dependency on another step
                    dependencies.add(dependency_id)
                else:
                    raise ValueError(f"Invalid input source '{source}' for step '{step_id}'")

            self.step_dependencies[step_id] = list(dependencies)

    async def run(self):
        """Execute the pipeline steps considering their dependencies."""
        if self.initial_params is None:
            raise ValueError("Initial parameters must be provided to run the pipeline.")

        # Set initial global inputs from provided params
        for key, value in self.initial_params.items():
            if key in self.global_inputs:
                self.global_inputs[key] = value

        completed_steps = set()

        # Identify all steps without dependencies
        initial_steps = self._get_initial_steps()
        print(f"Initial steps: {initial_steps}")

        with ThreadPoolExecutor() as executor:
            futures = {}
            # Start all initial steps with the initial_params
            for step_id in initial_steps:
                futures[step_id] = executor.submit(self.run_step, step_id, self.initial_params)

            while len(completed_steps) < len(self.step_instances):
                # Identify steps that are ready to run (all dependencies are met)
                ready_to_run = [
                    step_id for step_id, deps in self.step_dependencies.items()
                    if step_id not in completed_steps and all(dep in completed_steps for dep in deps)
                ]

                for step_id in ready_to_run:
                    print(f"Step '{step_id}' is ready to run.")
                    if step_id not in futures:
                        print(f"Starting step: {step_id}")
                        futures[step_id] = executor.submit(self.run_step, step_id, None)

                # Collect results as they complete, handling exceptions if they occur
                for future in as_completed(futures.values()):
                    step_id = [k for k, v in futures.items() if v == future][0]

                    try:
                        # This will re-raise any exceptions that occurred in the step
                        future.result()
                    except Exception as e:
                        print(f"Exception occurred in step '{step_id}': {e}")
                        raise e  # Re-raise the exception to be handled by the caller

                    completed_steps.add(step_id)
                    futures.pop(step_id)  # Remove from the list of running futures

        print("Pipeline execution completed.")

        return self.get_output()

    def run_step(self, step_id: str, initial_params: Dict[str, Any] = None):
        step = self.step_instances[step_id]
        input_data = initial_params if initial_params is not None else self.prepare_input_for_step(step)

        self.validate_inputs(step, input_data)

        self.push_update(f"Running step '{step.get_name()}'...")

        if inspect.iscoroutinefunction(step.process):
            result = asyncio.run(step.process(**input_data))
        else:
            result = step.process(**input_data)

        self.push_update(f"Step '{step.get_name()}' completed.")

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

    def validate_input_references(self, inputs: Dict[str, str], step_id: str):
        """Ensure all input references for a step contain a dot and reference valid sources."""
        for source in inputs.values():
            if '.' not in source:
                raise ValueError(f"Input source '{source}' for step '{step_id}' must contain a dot.")
            prefix, _ = source.split('.', 1)
            if prefix != 'inputs' and prefix not in self.step_instances:
                raise ValueError(f"Invalid input source '{source}' for step '{step_id}'. Must reference a global input or a valid step.")

    def prepare_input_for_step(self, step: PipelineStep) -> Dict[str, Any]:
        """Prepare the input for a step based on its dependencies and expected input type."""
        step_id = step.get_unique_id()
        inputs = {}

        # Map the outputs from dependencies or global inputs to the named inputs
        for input_name, source in step.inputs.items():
            if source.startswith('inputs.'):
                # Handle global pipeline input mapping
                global_input_key = source.split('.', 1)[1]
                inputs[input_name] = self.global_inputs.get(global_input_key)
            elif '.' in source:
                # Handle dependencies between steps
                dependency_id, field_name = source.split('.')
                result = self.step_results.get(dependency_id)

                # Handle both dict and object outputs
                if isinstance(result, dict):
                    inputs[input_name] = result.get(field_name)
                else:
                    inputs[input_name] = getattr(result, field_name, None)
            else:
                raise ValueError(f"Invalid input source '{source}' for step '{step_id}' - must contain a dot")

        return inputs  # Return a dictionary of named arguments

    def _get_initial_steps(self) -> List[str]:
        """Find all steps that have no dependencies or only depend on global inputs."""
        initial_steps = []
        for step_id, deps in self.step_dependencies.items():
            if not deps:  # No dependencies
                initial_steps.append(step_id)
            else:
                # Check if all dependencies are from global inputs
                if all(dep == 'inputs' for dep in deps):
                    initial_steps.append(step_id)
        return initial_steps

    def get_step_result(self, step_id: str) -> Any:
        """Retrieve the result of a given step."""
        return self.step_results.get(step_id)

    def get_output(self) -> Dict[str, Any]:
        """Retrieve the outputs based on the pipeline configuration."""
        outputs = {}
        for output_name, mapping in self.output_mapping.items():
            if mapping.startswith('inputs.'):
                # Handle output that is directly mapped to a global input
                global_input_key = mapping.split('.', 1)[1]
                outputs[output_name] = self.global_inputs.get(global_input_key)
            else:
                # Handle output that comes from step results
                step_id, field_name = mapping.split('.')
                result = self.get_step_result(step_id)
                if isinstance(result, dict):
                    outputs[output_name] = result.get(field_name)
                else:
                    outputs[output_name] = getattr(result, field_name, None)
        return outputs

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
