import inspect
import json
import os
import importlib.util
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, List, Any
import asyncio

from server.job_manager import Job
from server.nested_pipeline_step import NestedPipelineStep
from server.pipeline_metadata_extractor import PipelineStepsMetadataExtractor
from server.pipeline_step import PipelineStep


class Pipeline(Job):
    def __init__(self, job_id: str, definition: Dict[str, Any], steps_folder: str, pipelines_folder: str, initial_params: Dict[str, Any], pipeline_context: Dict[str, Any] = None):
        super().__init__(job_id=job_id)
        self.steps_folder = steps_folder
        self.pipelines_folder = pipelines_folder

        self.step_instances: Dict[str, PipelineStep] = {}
        self.step_dependencies: Dict[str, List[str]] = {}
        self.step_results: Dict[str, Any] = {}
        self.pipeline_context = pipeline_context or {}
        self.global_inputs: Dict[str, Any] = {}
        self.initial_params = initial_params
        self.properties: Dict[str, Any] = {}
        self.output_mapping: Dict[str, str] = {}
        self.step_labels: Dict[str, str] = {}
        self.steps_definitions: Dict[str, Dict[str, Any]] = {}
        self.pipeline_definitions: Dict[str, Dict[str, Any]] = {}

        self.discover_steps(steps_folder)
        self.discover_pipelines(pipelines_folder)
        print(f"Discovered steps: {self.pipeline_definitions}")
        print(f"Discovered pipelines: {self.pipeline_definitions}")

        self.create_pipeline_from_json(definition)

    def discover_steps(self, folder: str):
        extractor = PipelineStepsMetadataExtractor(folder, folder)
        extracted_steps_metadata = extractor.extract_pipeline_steps()

        for step_metadata in extracted_steps_metadata:
            step_type = step_metadata['type']
            self.steps_definitions[step_type] = step_metadata

    def discover_pipelines(self, folder: str):
        for dirpath, _, filenames in os.walk(folder):
            for filename in filenames:
                if filename.endswith(".json"):
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, 'r') as file:
                        try:
                            pipeline_data = json.load(file)
                            pipeline_id = pipeline_data.get("id")
                            self.pipeline_definitions[pipeline_id] = pipeline_data
                        except json.JSONDecodeError:
                            print(f"Failed to parse JSON in {file_path}")

    def create_pipeline_from_json(self, config: Dict[str, Any]):
        self.global_inputs = {
            input_name: input_value if input_value is not None else None
            for input_name, input_value in config.get("inputs", {}).items()
        }
        self.output_mapping = config.get("outputs", {})

        # Extract step IDs from the configuration
        step_ids = {step["id"] for step in config["steps"]}

        for step_config in config["steps"]:
            step_id = step_config.get("id")
            step_type = step_config.get("type")
            step_label = step_config.get("label", None)
            inputs = step_config.get("inputs", {})
            step_instance_config = step_config.get("config", {})

            # Validate input references using extracted step IDs
            self.validate_input_references(inputs, step_id, step_ids)

            print(f"Creating step instance for step '{step_id}' of type '{step_type}'")

            # Handle all steps using metadata
            if step_type in self.steps_definitions or step_type == "pipeline":
                if step_type == "pipeline":
                    pipeline_id = step_instance_config.get("pipeline_id")
                    # Use the metadata to resolve inputs
                    print(f"Creating nested pipeline step with definition: {pipeline_id}")
                    # nested_pipeline_inputs = {
                    #     input_key: self.global_inputs.get(input_value.split('.', 1)[1], None)
                    #     if input_value.startswith('inputs.') else self.step_results.get(input_value.split('.')[0], {}).get(input_value.split('.')[1], None)
                    #     for input_key, input_value in inputs.items()
                    # }
                    # print(f"Resolved inputs for nested pipeline: {nested_pipeline_inputs}")
                    step_instance = NestedPipelineStep(
                        pipeline=self,
                        definition=self.pipeline_definitions.get(pipeline_id)
                    )
                    print(f"Created nested pipeline step instance: {step_instance}")
                    step_instance.inputs = inputs
                    print(f"Set inputs for nested pipeline step instance: {step_instance.inputs}")
                else:
                    step_class = self.steps_definitions.get(step_type).get('class')
                    step_module = self.steps_definitions.get(step_type).get('module')
                    module = importlib.import_module(step_module)
                    full_class_name = getattr(module, step_class)
                    step_instance = full_class_name(pipeline=self, **step_instance_config, **self.pipeline_context)
                    step_instance.inputs = inputs

                if step_label:
                    self.step_labels[step_id] = step_label

                print(f"Created step instance for step '{step_id}' of type '{step_type}'")

                # Register the step instance using its unique ID
                self.register_step(step_instance, step_id)
            else:
                raise ValueError(f"Step ID '{step_type}' not found in the extracted steps metadata.")

        print(f"Step instances: {self.step_instances}")

        self._resolve_dependencies(step_ids)

    def _resolve_references_in_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        resolved_config = {}
        for key, value in config.items():
            resolved_config[key] = value
        return resolved_config

    def register_step(self, step: PipelineStep, step_id: str):
        # Register the step instance with its unique ID
        self.step_instances[step_id] = step
        self.step_dependencies[step_id] = []

        print(f"Registered step '{step_id}'")

    def _resolve_dependencies(self, step_ids: set):
        for step_id, step_instance in self.step_instances.items():
            print(f"Resolving dependencies for step '{step_id}'")
            inputs = step_instance.inputs
            print(f"Inputs for step '{step_id}': {inputs}")
            dependencies = set()

            for input_name, source in inputs.items():
                print(f"Processing input '{input_name}' with source '{source}'")
                if '.' in source:
                    parts = source.split('.')
                    if len(parts) == 2:
                        dependency_id, _ = parts
                    else:
                        raise ValueError(f"Invalid input source format '{source}' for step '{step_id}'")
                else:
                    raise ValueError(f"Invalid input source '{source}' for step '{step_id}' - must contain a dot")

                # Check against 'inputs' or valid step IDs from the configuration
                if dependency_id == 'inputs':
                    dependencies.add('inputs')
                elif dependency_id in step_ids:
                    dependencies.add(dependency_id)
                else:
                    raise ValueError(f"Invalid input source '{source}' for step '{step_id}'")

            self.step_dependencies[step_id] = list(dependencies)

    async def run(self):
        if self.initial_params is None:
            raise ValueError("Initial parameters must be provided to run the pipeline.")

        print("Running pipeline...")

        # Initialize global inputs
        for key, value in self.initial_params.items():
            if key in self.global_inputs:
                self.global_inputs[key] = value

        # Dictionary to track completed steps
        completed_steps = set()

        # Identify initial steps that have no dependencies or only depend on inputs
        steps_to_run = self._get_initial_steps()

        with ThreadPoolExecutor() as executor:
            while steps_to_run:
                futures = {}

                # Prepare and submit steps for execution
                for step_id in steps_to_run:
                    if step_id not in completed_steps:  # Ensure the step hasn't been completed
                        step_instance = self.step_instances[step_id]
                        step_inputs = self.prepare_input_for_step(step_instance)
                        futures[step_id] = executor.submit(self.run_step, step_id, step_inputs)

                # Wait for any step to complete
                for future in as_completed(futures.values()):
                    step_id = next(k for k, v in futures.items() if v == future)
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Exception occurred in step '{step_id}': {e}")
                        raise e

                    # Mark the step as completed after successful execution
                    completed_steps.add(step_id)

                print(f"Completed steps: {completed_steps}")

                # Determine which steps are ready to run next
                steps_to_run = []
                print("Checking dependencies for next steps...")
                for step_id, deps in self.step_dependencies.items():
                    if step_id not in completed_steps:
                        # Check if all dependencies for this step have been completed

                        print(f"Checking dependencies for step '{step_id}': {deps}")

                        all_deps_completed = all(
                            dep in completed_steps or dep == 'inputs' for dep in deps
                        )
                        if all_deps_completed:
                            print(f"Step '{step_id}' is ready to run: all dependencies {deps} are completed or are global inputs.")
                            steps_to_run.append(step_id)
                        else:
                            print(f"Step '{step_id}' is not ready to run: dependencies {deps} are not yet completed.")
                print(f"Next steps to run: {steps_to_run}")

        return self.get_output()

    def _get_dependent_steps(self, step_id: str) -> List[str]:
        """Find all steps that depend directly on the given step."""
        return [
            dependent_id for dependent_id, deps in self.step_dependencies.items()
            if step_id in deps
        ]

    def run_step(self, step_id: str, initial_params: Dict[str, Any] = None):
        step = self.step_instances[step_id]

        print(f"Running step '{step_id}' with initial params: {initial_params}")

        input_data = initial_params if initial_params is not None else self.prepare_input_for_step(step)

        print(f"Prepared input data for step '{step_id}': {input_data}")

        self.validate_inputs(step, input_data)

        print(f"Validated inputs for step '{step_id}'")

        # Use the label for updates if available; otherwise, use the step name
        step_label = self.step_labels.get(step_id, step.get_name())
        self.push_update(f"Running step '{step_label}'...")

        if inspect.iscoroutinefunction(step.process):
            print(f"Running step '{step_id}' asynchronously...")
            result = asyncio.run(step.process(**input_data))
        else:
            print(f"Running step '{step_id}' synchronously...")
            result = step.process(**input_data)

        print(f"Step '{step_id}' completed execution.")
        self.push_update(f"Step '{step_label}' completed.")
        self.step_results[step_id] = result

    def validate_inputs(self, step: PipelineStep, input_data: Dict[str, Any]):
        step_type = step.get_type()
        print(f"Validating inputs for step '{step.get_name()}' of type '{step_type}'")
        print(f"Step definitions: {self.steps_definitions}")

        if isinstance(step, NestedPipelineStep):
            # If the step is a nested pipeline, retrieve the nested pipeline's definition
            nested_pipeline_def = self.pipeline_definitions.get(step.definition.get("id"))
            if not nested_pipeline_def:
                raise ValueError(f"Definition for nested pipeline '{step.get_name()}' not found.")

            # Extract required inputs from the nested pipeline definition
            required_inputs = nested_pipeline_def.get('inputs', [])
        else:
            # For regular steps, get the required inputs from step definitions
            required_inputs = self.steps_definitions[step_type].get('inputs', [])

        print(f"Required inputs for step '{step.get_name()}': {required_inputs}")
        missing_inputs = [input_name for input_name in required_inputs if input_name not in input_data]
        print(f"Missing inputs for step '{step.get_name()}': {missing_inputs}")

        if missing_inputs:
            raise ValueError(f"Missing required inputs for step '{step.get_name()}': {', '.join(missing_inputs)}")

    def validate_input_references(self, inputs: Dict[str, str], step_id: str, step_ids: set):
        for source in inputs.values():
            if '.' not in source:
                raise ValueError(f"Input source '{source}' for step '{step_id}' must contain a dot.")

            prefix, _ = source.split('.', 1)

            # Check if the prefix is either 'inputs' or matches a valid step ID from the configuration
            if prefix != 'inputs' and prefix not in step_ids:
                raise ValueError(f"Invalid input source '{source}' for step '{step_id}'. Must reference a global input or a valid step defined in the pipeline.")

    def prepare_input_for_step(self, step: PipelineStep) -> Dict[str, Any]:
        step_id = step.get_type()
        inputs = {}

        print(f"Preparing inputs for step '{step_id}'")

        for input_name, source in step.inputs.items():
            print(f"Processing input '{input_name}' for step '{step_id}' with source '{source}'")
            if source.startswith('inputs.'):
                print(f"Global inputs: {self.global_inputs}")
                global_input_key = source.split('.', 1)[1]
                print(f"Global input key: {global_input_key}")
                inputs[input_name] = self.global_inputs.get(global_input_key)
                print(f"Input for step '{step_id}': {input_name} = {inputs[input_name]}")
            elif '.' in source:
                dependency_id, field_name = source.split('.')
                result = self.step_results.get(dependency_id)

                if isinstance(result, dict):
                    inputs[input_name] = result.get(field_name)
                else:
                    inputs[input_name] = getattr(result, field_name, None)
            else:
                raise ValueError(f"Invalid input source '{source}' for step '{step_id}' - must contain a dot")

        return inputs

    def _get_initial_steps(self) -> List[str]:
        initial_steps = []
        for step_id, deps in self.step_dependencies.items():
            if not deps:
                initial_steps.append(step_id)
            else:
                if all(dep == 'inputs' for dep in deps):
                    initial_steps.append(step_id)
        return initial_steps

    def get_step_result(self, step_id: str) -> Any:
        return self.step_results.get(step_id)

    def get_output(self) -> Dict[str, Any]:
        outputs = {}
        for output_name, mapping in self.output_mapping.items():
            if mapping.startswith('inputs.'):
                global_input_key = mapping.split('.', 1)[1]
                outputs[output_name] = self.global_inputs.get(global_input_key)
            else:
                step_id, field_name = mapping.split('.')
                result = self.get_step_result(step_id)
                if isinstance(result, dict):
                    outputs[output_name] = result.get(field_name)
                else:
                    outputs[output_name] = getattr(result, field_name, None)
        return outputs
