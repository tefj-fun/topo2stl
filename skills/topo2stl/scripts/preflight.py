#!/usr/bin/env python3
"""Validate Topo2STL project inputs and print the load table."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: python -m pip install pyyaml")


REQUIRED_PATHS = (
    ("project", "name"),
    ("project", "revision"),
    ("geometry", "design_domain"),
    ("geometry", "final_stl"),
    ("loading", "payload_mass_kg"),
    ("loading", "center_of_gravity_mm"),
    ("loading", "safety_factor"),
    ("loading", "restraints"),
    ("loading", "cases"),
    ("material", "name"),
    ("printer", "nozzle_mm"),
    ("printer", "line_width_mm"),
    ("printer", "layer_height_mm"),
    ("printer", "walls"),
    ("printer", "infill_percent"),
    ("optimization", "method"),
    ("optimization", "target_volume_fraction"),
    ("acceptance", "maximum_displacement_mm"),
    ("acceptance", "minimum_p99_directional_fos"),
)


def nested(data: dict, path: tuple[str, ...]):
    value = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def vector3(value, label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or len(value) != 3 or not all(isinstance(v, (int, float)) for v in value):
        errors.append(f"{label} must be a three-number list")


def load_config(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("configuration root must be a mapping")
    return data


def validate(data: dict, config_path: Path, check_paths: bool) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_PATHS:
        value = nested(data, path)
        if value is None or value == "" or value == []:
            errors.append(f"missing {'.'.join(path)}")

    vector3(nested(data, ("loading", "center_of_gravity_mm")), "loading.center_of_gravity_mm", errors)
    cases = nested(data, ("loading", "cases")) or []
    seen: set[str] = set()
    for index, case in enumerate(cases):
        label = f"loading.cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be a mapping")
            continue
        case_id = case.get("id")
        if not case_id:
            errors.append(f"{label}.id is required")
        elif case_id in seen:
            errors.append(f"duplicate load case id: {case_id}")
        else:
            seen.add(case_id)
        vector3(case.get("force_n"), f"{label}.force_n", errors)
        vector3(case.get("moment_nm"), f"{label}.moment_nm", errors)
        if not case.get("application_region"):
            errors.append(f"{label}.application_region is required")

    volume = nested(data, ("optimization", "target_volume_fraction"))
    if isinstance(volume, (int, float)) and not 0 < volume <= 1:
        errors.append("optimization.target_volume_fraction must be in (0, 1]")
    infill = nested(data, ("printer", "infill_percent"))
    if isinstance(infill, (int, float)) and not 0 <= infill <= 100:
        errors.append("printer.infill_percent must be between 0 and 100")

    if check_paths:
        base = config_path.parent
        for path in (("geometry", "design_domain"), ("geometry", "final_stl")):
            value = nested(data, path)
            if isinstance(value, str) and not (base / value).exists():
                errors.append(f"path does not exist: {value}")
    return errors


def print_load_table(data: dict) -> None:
    loading = data["loading"]
    print(f"Payload: {loading['payload_mass_kg']} kg")
    print(f"Center of gravity: {loading['center_of_gravity_mm']} mm")
    print(f"Required safety factor: {loading['safety_factor']}")
    print("\nLoad cases:")
    print("id | force N [x,y,z] | moment N*m [x,y,z] | application")
    print("---|---|---|---")
    for case in loading["cases"]:
        print(f"{case['id']} | {case['force_n']} | {case['moment_nm']} | {case['application_region']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--check-paths", action="store_true", help="require declared geometry paths to exist")
    args = parser.parse_args()
    try:
        data = load_config(args.config)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    errors = validate(data, args.config, args.check_paths)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print_load_table(data)
    print("\nPASS: project inputs are complete; show this load table to the user for confirmation before solving.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
