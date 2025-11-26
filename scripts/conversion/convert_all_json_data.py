"""Recursively convert all JSON files under data/json/ to YAML files under data/yaml/.

This script preserves the relative directory structure. Example:
  data/json/entities/foo.json -> data/yaml/entities/foo.yaml

Usage:
  python scripts/convert_all_json_data.py [--data-root DATA_ROOT] [--dry-run] [--overwrite]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Iterator

import yaml
from pathlib import PurePath
import importlib.util
import types


# Try to import convert_file from convert_json2yaml in the same scripts/ directory.
def _load_convert_file() -> types.FunctionType:
    try:
        # First try a normal package import (if scripts is a package)
        from convert_json2yaml import convert_file  # type: ignore

        return convert_file
    except Exception:
        # Fallback: load module by path relative to this file
        this_dir = Path(__file__).resolve().parent
        candidate = this_dir / "convert_json2yaml.py"
        if not candidate.exists():
            raise ImportError("Cannot find convert_json2yaml.py next to convert_all_json_data.py")

        spec = importlib.util.spec_from_file_location("convert_json2yaml", str(candidate))
        if spec is None or spec.loader is None:
            raise ImportError("Failed to load spec for convert_json2yaml.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        if not hasattr(mod, "convert_file"):
            raise ImportError("convert_json2yaml.py does not define convert_file")
        return getattr(mod, "convert_file")


_convert_file = _load_convert_file()


def iter_json_files(root: Path) -> Iterator[Path]:
    for p in root.rglob("*.json"):
        # skip hidden dirs/files
        if any(part.startswith(".") for part in p.parts):
            continue
        yield p


def convert_all(data_root: Path, dry_run: bool = False, overwrite: bool = False) -> int:
    json_root = data_root / "json"
    yaml_root = data_root / "yaml"

    if not json_root.exists():
        print(f"No json directory found at {json_root}")
        return 1

    count = 0
    for jpath in iter_json_files(json_root):
        rel = jpath.relative_to(json_root)
        out_path = (yaml_root / rel).with_suffix(".yaml")

        print(f"Converting {jpath} -> {out_path}")
        if dry_run:
            continue

        try:
            # delegate to convert_json2yaml.convert_file
            if dry_run:
                # still validate by loading the JSON
                with jpath.open("r", encoding="utf-8") as f:
                    _ = json.load(f)
                # show where it would write
                print(f"[dry-run] would write: {out_path}")
            else:
                _convert_file(jpath, out_path, overwrite=overwrite)
                count += 1
        except FileExistsError:
            print(f"Skipping existing file {out_path} (use --overwrite to replace)")
            continue
        except Exception as e:
            print(f"Failed to convert {jpath}: {e}")
            continue

    print(f"Completed. Converted {count} file(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert all JSON under data/json/ to data/yaml/")
    parser.add_argument("--data-root", default="data", help="Path to data root (default: data)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files; just show what would be done")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing YAML files")

    args = parser.parse_args(argv)
    data_root = Path(args.data_root)
    try:
        return convert_all(data_root, dry_run=args.dry_run, overwrite=args.overwrite)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
