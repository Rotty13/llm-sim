"""Convert a JSON file to YAML.

Usage:
    python scripts/convert_json2yaml.py input.json [output.yaml] [--overwrite]

If output path is omitted, the output file will be created next to the input with .yaml extension.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml


def convert_file(input_path: Path, output_path: Path, overwrite: bool = False) -> Path:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output file already exists: {output_path} (use --overwrite to replace)")

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure parent dir exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Use safe_dump to avoid arbitrary python objects
    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert JSON file to YAML")
    parser.add_argument("input", help="Input JSON file path")
    parser.add_argument("output", nargs="?", help="Output YAML file path (optional)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output file")

    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".yaml")

    try:
        out = convert_file(input_path, output_path, overwrite=args.overwrite)
        print(f"Wrote: {out}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
