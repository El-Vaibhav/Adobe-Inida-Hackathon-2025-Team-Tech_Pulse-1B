#!/usr/bin/env python3
"""
Schema validation script for Challenge 1B output
Adobe India Hackathon 2025 🏆
"""

import json
import sys
from pathlib import Path
import jsonschema
from typing import List

def color_text(text, color):
    """
    Color text for terminal output.

    Args:
        text (str): Text to color.
        color (str): Color name.

    Returns:
        str: Colored text.
    """
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def get_schema_path() -> Path:
    """
    Get the path to the schema file.

    Returns:
        Path: Path to the schema file.
    """
    return Path(__file__).parent / "challenge1b_output_schema.json"

def read_json_file(file_path: Path) -> dict:
    """
    Read a JSON file.

    Args:
        file_path (Path): Path to the JSON file.

    Returns:
        dict: The loaded JSON data.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_schema_load_error(e, schema_path):
    """
    Print an error message for schema loading issues.

    Args:
        e (Exception): The exception that occurred.
        schema_path (Path): Path to the schema file.
    """
    print(color_text(f"❌ Schema file error: {e} ({schema_path})", "red"))
    sys.exit(1)

def load_schema() -> dict:
    """
    Load the JSON schema for validation.

    Returns:
        dict: The loaded schema.
    """
    schema_path = get_schema_path()
    try:
        return read_json_file(schema_path)
    except FileNotFoundError as e:
        print_schema_load_error("not found", schema_path)
    except json.JSONDecodeError as e:
        print_schema_load_error(f"invalid JSON: {e}", schema_path)

def check_sections_and_subsections(output_data: dict):
    """
    Check if sections and subsections are present in the output data.

    Args:
        output_data (dict): The output data to check.
    """
    sections = output_data.get('extracted_sections', [])
    subsections = output_data.get('subsection_analysis', [])
    if not sections and not subsections:
        print(color_text("  ⚠️  Warning: No sections or subsections found", "yellow"))

def check_importance_ranks(sections):
    """
    Check if importance ranks are sequential.

    Args:
        sections (list): List of sections to check.
    """
    ranks = [s.get('importance_rank', 0) for s in sections]
    if ranks and ranks != sorted(ranks):
        print(color_text("  ⚠️  Warning: Importance ranks are not sequential", "yellow"))

def semantic_checks(output_data: dict):
    """
    Perform semantic checks on the output data.

    Args:
        output_data (dict): The output data to check.
    """
    check_sections_and_subsections(output_data)
    sections = output_data.get('extracted_sections', [])
    if sections:
        check_importance_ranks(sections)

def validate_json_schema(output_data: dict, schema: dict):
    """
    Validate JSON data against a schema.

    Args:
        output_data (dict): The JSON data to validate.
        schema (dict): The schema to validate against.

    Returns:
        tuple: (bool, str) indicating validity and error message.
    """
    try:
        jsonschema.validate(instance=output_data, schema=schema)
        return True, ""
    except jsonschema.ValidationError as e:
        return False, f"{e.message}\n      Path: {' -> '.join(str(p) for p in e.path)}"

def validate_output_file(file_path: Path, schema: dict) -> bool:
    """
    Validate an output file against the schema.

    Args:
        file_path (Path): Path to the output file.
        schema (dict): The schema to validate against.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    try:
        output_data = read_json_file(file_path)
    except FileNotFoundError:
        print(color_text(f"  ❌ File not found: {file_path}", "red"))
        return False
    except json.JSONDecodeError as e:
        print(color_text(f"  ❌ Invalid JSON: {e}", "red"))
        return False

    valid, error_msg = validate_json_schema(output_data, schema)
    if not valid:
        print(color_text(f"  ❌ Schema validation error: {error_msg}", "red"))
        return False

    semantic_checks(output_data)
    print(color_text("  ✅ Valid JSON structure", "green"))
    print(color_text("  🌟 Perfect compliance!", "blue"))
    return True

def get_output_patterns() -> List[str]:
    """
    Get the output file patterns to search for.

    Returns:
        List[str]: List of output file patterns.
    """
    return [
        "challenge1b_output*.json",
        "*output*.json",
        "round_1b*.json"
    ]

def find_output_files(directory: Path) -> List[Path]:
    """
    Find output files in the directory matching patterns.

    Args:
        directory (Path): Directory to search in.

    Returns:
        List[Path]: List of found output files.
    """
    files = []
    for pattern in get_output_patterns():
        files.extend(directory.glob(pattern))
    return sorted(set(files))

def print_summary(valid_files, total_files):
    """
    Print a summary of validation results.

    Args:
        valid_files (int): Number of valid files.
        total_files (int): Total number of files.
    """
    print("\n" + "=" * 40)
    print(color_text("Validation Summary:", "blue"))
    valid_ratio = f"{valid_files}/{total_files}"
    color = 'green' if valid_files == total_files else 'yellow'
    print(f"   Valid files: {color_text(valid_ratio, color)}")
    if valid_files == total_files:
        print(color_text("   🎉 All files passed validation!", "green"))
    else:
        print(color_text(f"   ⚠️  {total_files - valid_files} file(s) failed validation", "yellow"))

def get_files_to_validate(argv, output_dir: Path) -> List[Path]:
    """
    Get the list of files to validate.

    Args:
        argv (List[str]): Command line arguments.
        output_dir (Path): Default output directory.

    Returns:
        List[Path]: List of files to validate.
    """
    if len(argv) > 1:
        return [Path(arg) for arg in argv[1:]]
    return find_output_files(output_dir)

def main():
    """
    Main function to validate output files.
    """
    print(color_text("📜 Challenge 1B Output Validator", "blue"))
    print("=" * 40)
    schema = load_schema()
    print(color_text("📋 Schema loaded successfully", "green"))
    output_dir = Path(__file__).parent / "output"
    files_to_validate = get_files_to_validate(sys.argv, output_dir)

    if not files_to_validate:
        print(color_text("❌ No output files found to validate", "red"))
        return 1

    print(color_text(f"🔍 Found {len(files_to_validate)} output file(s)", "blue"))
    valid_files = 0
    total_files = len(files_to_validate)

    for file_path in files_to_validate:
        print(f"\n{color_text('🔎 Validating:', 'blue')} {file_path.name}")
        if validate_output_file(file_path, schema):
            valid_files += 1

    print_summary(valid_files, total_files)
    return 0 if valid_files == total_files else 1

if __name__ == "__main__":
    sys.exit(main())
