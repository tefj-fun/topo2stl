#!/usr/bin/env python3
"""Validate a Topo2STL release manifest and final STL."""

from __future__ import annotations

import argparse
from collections import Counter, deque
import json
import math
from pathlib import Path
import re
import struct
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: python -m pip install pyyaml")


Vec3 = tuple[float, float, float]
Triangle = tuple[Vec3, Vec3, Vec3]


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be an object")
    return data


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be a mapping")
    return data


def load_stl(path: Path) -> list[Triangle]:
    raw = path.read_bytes()
    if len(raw) >= 84:
        count = struct.unpack_from("<I", raw, 80)[0]
        if 84 + count * 50 == len(raw):
            triangles = []
            for offset in range(84, len(raw), 50):
                values = struct.unpack_from("<12fH", raw, offset)
                triangles.append((tuple(values[3:6]), tuple(values[6:9]), tuple(values[9:12])))
            return triangles

    text = raw.decode("utf-8", errors="ignore")
    vertices = [tuple(map(float, match)) for match in re.findall(
        r"\bvertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", text
    )]
    if not vertices or len(vertices) % 3:
        raise ValueError("STL is neither a consistent binary STL nor a parseable ASCII STL")
    return [tuple(vertices[i:i + 3]) for i in range(0, len(vertices), 3)]


def rounded(vertex: Vec3) -> Vec3:
    return tuple(round(float(value), 6) for value in vertex)


def edge(a: Vec3, b: Vec3) -> tuple[Vec3, Vec3]:
    a, b = rounded(a), rounded(b)
    return (a, b) if a <= b else (b, a)


def signed_volume(triangle: Triangle) -> float:
    a, b, c = triangle
    cross = (
        b[1] * c[2] - b[2] * c[1],
        b[2] * c[0] - b[0] * c[2],
        b[0] * c[1] - b[1] * c[0],
    )
    return (a[0] * cross[0] + a[1] * cross[1] + a[2] * cross[2]) / 6.0


def area2(triangle: Triangle) -> float:
    a, b, c = triangle
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ac = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    cross = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )
    return math.sqrt(sum(value * value for value in cross))


def stl_stats(triangles: list[Triangle]) -> dict:
    if not triangles:
        raise ValueError("STL has no triangles")
    edge_counts: Counter = Counter()
    edge_faces: dict[tuple[Vec3, Vec3], list[int]] = {}
    vertices: list[Vec3] = []
    degenerate = 0
    for index, triangle in enumerate(triangles):
        vertices.extend(triangle)
        if area2(triangle) <= 1e-12:
            degenerate += 1
        for current in (edge(triangle[0], triangle[1]), edge(triangle[1], triangle[2]), edge(triangle[2], triangle[0])):
            edge_counts[current] += 1
            edge_faces.setdefault(current, []).append(index)

    adjacency = [set() for _ in triangles]
    for faces in edge_faces.values():
        for face in faces[1:]:
            adjacency[faces[0]].add(face)
            adjacency[face].add(faces[0])
    unseen = set(range(len(triangles)))
    components = 0
    while unseen:
        components += 1
        queue = deque([unseen.pop()])
        while queue:
            for neighbor in adjacency[queue.popleft()]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)

    bounds = []
    for axis in range(3):
        values = [vertex[axis] for vertex in vertices]
        bounds.append([min(values), max(values)])
    return {
        "triangles": len(triangles),
        "components": components,
        "boundary_edges": sum(count == 1 for count in edge_counts.values()),
        "nonmanifold_edges": sum(count > 2 for count in edge_counts.values()),
        "degenerate_triangles": degenerate,
        "watertight": all(count == 2 for count in edge_counts.values()),
        "volume_mm3": abs(sum(signed_volume(triangle) for triangle in triangles)),
        "bounds_mm": bounds,
    }


def resolve(base: Path, value: str) -> Path:
    return (base / value).resolve()


def existing_path(base: Path, value, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"missing {label}")
        return None
    path = resolve(base, value)
    if not path.is_file():
        errors.append(f"missing file for {label}: {value}")
        return None
    return path


def validate(manifest_path: Path) -> tuple[list[str], dict | None]:
    errors: list[str] = []
    manifest = load_json(manifest_path)
    base = manifest_path.parent
    config_path = existing_path(base, manifest.get("project_config"), "project_config", errors)
    if not config_path:
        return errors, None
    config = load_yaml(config_path)
    acceptance = config.get("acceptance", {})
    artifacts = manifest.get("artifacts", {})
    if not isinstance(artifacts, dict):
        errors.append("artifacts must be an object")
        return errors, None

    stl_path = existing_path(base, artifacts.get("final_stl"), "artifacts.final_stl", errors)
    existing_path(base, artifacts.get("fea_results"), "artifacts.fea_results", errors)
    existing_path(base, artifacts.get("slicer_output"), "artifacts.slicer_output", errors)

    results = manifest.get("results", {})
    checks = (
        ("maximum_displacement_mm", "maximum_displacement_mm", lambda actual, limit: actual <= limit, "exceeds"),
        ("minimum_p99_directional_fos", "minimum_p99_directional_fos", lambda actual, limit: actual >= limit, "is below"),
        ("volume_error_percent", "maximum_volume_error_percent", lambda actual, limit: actual <= limit, "exceeds"),
    )
    for result_key, limit_key, passes, wording in checks:
        actual, limit = results.get(result_key), acceptance.get(limit_key)
        if not isinstance(actual, (int, float)):
            errors.append(f"results.{result_key} must be numeric")
        elif not isinstance(limit, (int, float)):
            errors.append(f"acceptance.{limit_key} must be numeric")
        elif not passes(actual, limit):
            errors.append(f"{result_key} {actual} {wording} acceptance {limit}")

    visuals = manifest.get("visual_evidence", {})
    if not isinstance(visuals, dict):
        errors.append("visual_evidence must be an object")
        visuals = {}
    for key in ("load_map", "before", "after", "slicer_preview"):
        existing_path(base, visuals.get(key), f"visual_evidence.{key}", errors)
    progress = visuals.get("optimization_progress", [])
    minimum_progress = acceptance.get("minimum_progress_images", 4)
    if not isinstance(progress, list) or len(progress) < minimum_progress:
        errors.append(f"optimization_progress requires at least {minimum_progress} images")
    else:
        for index, item in enumerate(progress):
            if not isinstance(item, dict) or not item.get("stage"):
                errors.append(f"optimization_progress[{index}].stage is required")
                continue
            existing_path(base, item.get("path"), f"optimization_progress[{index}].path", errors)

    cases = {case.get("id") for case in config.get("loading", {}).get("cases", []) if isinstance(case, dict)}
    hotspots = visuals.get("fea_hotspots", [])
    hotspot_cases = set()
    if not isinstance(hotspots, list):
        errors.append("visual_evidence.fea_hotspots must be a list")
    else:
        for index, item in enumerate(hotspots):
            if not isinstance(item, dict) or not item.get("load_case"):
                errors.append(f"fea_hotspots[{index}].load_case is required")
                continue
            hotspot_cases.add(item["load_case"])
            existing_path(base, item.get("path"), f"fea_hotspots[{index}].path", errors)
    missing_cases = sorted(cases - hotspot_cases)
    if missing_cases:
        errors.append(f"missing FEA hotspot images for load cases: {', '.join(missing_cases)}")

    stats = None
    if stl_path:
        stats = stl_stats(load_stl(stl_path))
        if acceptance.get("require_watertight_stl") and not stats["watertight"]:
            errors.append("final STL is not watertight")
        if acceptance.get("require_single_component") and stats["components"] != 1:
            errors.append(f"final STL has {stats['components']} components")
        if stats["degenerate_triangles"]:
            errors.append(f"final STL has {stats['degenerate_triangles']} degenerate triangles")
        if stats["volume_mm3"] <= 0:
            errors.append("final STL has zero enclosed volume")
    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        errors, stats = validate(args.manifest.resolve())
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError, struct.error) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if stats:
        print(json.dumps({"stl": stats}, indent=2))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: release contract, evidence files, acceptance metrics, and STL integrity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
