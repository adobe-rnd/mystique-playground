import os
import json
from pathlib import Path
from hashlib import sha1
from urllib.parse import urlparse
from jsonschema import validate


def bundle_schemas(root_schema_path: str):
    def resolve_ref(ref, schema_map, current_file):
        parsed_ref = urlparse(ref)
        if parsed_ref.scheme == '':  # Local reference within a file
            ref_path = parsed_ref.path
            if ref_path:  # Reference to an external file
                abs_ref_path = (Path(current_file).parent / ref_path).resolve()
                ref_schema = schema_map.get(str(abs_ref_path))
                if ref_schema is None:
                    raise ValueError(f"Referenced schema {abs_ref_path} not found.")
                return ref_schema, str(abs_ref_path)
            else:  # Internal reference within the same file
                return None, None
        else:
            raise ValueError(f"Unsupported $ref scheme: {ref}")

    def generate_definition_name(file_path):
        """
        Generate a meaningful name for the schema definition based on the file name.
        """
        base_name = Path(file_path).stem.replace(" ", "_").lower()
        return base_name

    def bundle_schema(schema, schema_map, current_file, ref_map, definitions):
        """
        Bundles the schema by resolving only external $ref instances and converting them to internal references.
        """
        if isinstance(schema, dict):
            if "$ref" in schema:
                ref = schema["$ref"]
                resolved_schema, resolved_path = resolve_ref(ref, schema_map, current_file)
                if resolved_schema:
                    if resolved_path not in ref_map:
                        # Generate a descriptive name for the external schema
                        def_name = generate_definition_name(resolved_path)
                        ref_map[resolved_path] = def_name
                        definitions[def_name] = bundle_schema(resolved_schema, schema_map, resolved_path, ref_map, definitions)
                    return {"$ref": f"#/definitions/{ref_map[resolved_path]}"}
            else:
                # Process nested objects and arrays recursively
                for key, value in schema.items():
                    schema[key] = bundle_schema(value, schema_map, current_file, ref_map, definitions)
        elif isinstance(schema, list):
            return [bundle_schema(item, schema_map, current_file, ref_map, definitions) for item in schema]
        return schema

    def extract_definitions(ref_map, definitions):
        """
        Extracts the unique schemas stored in the ref_map into a definitions block.
        """
        return {v: definitions[v] for v in ref_map.values()}

    # Step 1: Read all schemas into a schema map.
    schema_map = {}
    root_schema_path = Path(root_schema_path).resolve()

    # Find and load all schema files
    for file in root_schema_path.parent.glob("*.json"):
        with open(file) as f:
            schema_map[str(file.resolve())] = json.load(f)

    # Step 2: Create maps for tracking reusable schemas and definitions
    ref_map = {}
    definitions = {}

    # Step 3: Start bundling from the root schema
    root_schema = schema_map[str(root_schema_path.resolve())]
    bundled_schema = bundle_schema(root_schema, schema_map, str(root_schema_path), ref_map, definitions)

    # Step 4: Extract definitions and include them in the bundled schema
    if ref_map:
        bundled_schema["definitions"] = extract_definitions(ref_map, definitions)

    return bundled_schema

