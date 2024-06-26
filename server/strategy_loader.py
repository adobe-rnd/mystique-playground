import importlib
import inspect
import sys
import os
import importlib.util
from types import ModuleType

from server.generation_strategies.base_strategy import AbstractGenerationStrategy


def dynamic_import_concrete_classes(folder_path):
    concrete_classes = []

    def _find_classes(module: ModuleType):
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, AbstractGenerationStrategy) and obj is not AbstractGenerationStrategy:
                concrete_classes.append(obj)

    def _import_module_from_path(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _import_submodules_from_folder(current_folder_path, package_prefix=""):
        if not os.path.isdir(current_folder_path):
            print(f"Error: The folder path {current_folder_path} does not exist.", file=sys.stderr)
            return

        for entry in os.scandir(current_folder_path):
            if entry.is_file() and entry.name.endswith('.py') and entry.name != '__init__.py':
                module_name = f"{package_prefix}{entry.name[:-3]}" if package_prefix else entry.name[:-3]
                try:
                    module = _import_module_from_path(module_name, entry.path)
                    _find_classes(module)
                except Exception as e:
                    print(f"Error importing {module_name}: {e}", file=sys.stderr)

            elif entry.is_dir():
                sub_package_prefix = f"{package_prefix}{entry.name}." if package_prefix else f"{entry.name}."
                _import_submodules_from_folder(entry.path, sub_package_prefix)

    _import_submodules_from_folder(folder_path)

    return concrete_classes


def load_generation_strategies():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, 'generation_strategies')

    classes = dynamic_import_concrete_classes(folder_path)

    strategies = []
    for cls in classes:
        try:
            strategy = cls()
            strategies.append((strategy.id(), strategy.name(), strategy.category(), cls))
        except Exception as e:
            print(f"Error instantiating {cls}: {e}", file=sys.stderr)

    return strategies


if __name__ == "__main__":
    # Get the strategies
    strategies = load_generation_strategies()
    print(f"Found {len(strategies)} generation strategy(s).")

    # Print the strategies
    for id, name, capabilities, cls in strategies:
        print(f"ID: {id}")
        print(f"Name: {name}")
        print(f"Capabilities: {capabilities}")
        print(f"Class: {cls}")
