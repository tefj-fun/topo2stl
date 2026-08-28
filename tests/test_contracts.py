from __future__ import annotations

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "topo2stl"
PREFLIGHT = SKILL / "scripts" / "preflight.py"
VALIDATE_RELEASE = SKILL / "scripts" / "validate-release.py"


def run_script(script: Path, *arguments: Path | str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *(str(value) for value in arguments)],
        text=True,
        capture_output=True,
        check=False,
    )


def write_cube(path: Path) -> None:
    vertices = [
        (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, 1.0), (0.0, 1.0, 1.0),
    ]
    faces = [
        (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
        (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7),
    ]
    data = bytearray(80)
    data.extend(struct.pack("<I", len(faces)))
    for face in faces:
        data.extend(struct.pack("<12fH", 0, 0, 0, *vertices[face[0]], *vertices[face[1]], *vertices[face[2]], 0))
    path.write_bytes(data)


class ContractTests(unittest.TestCase):
    def test_plugin_and_preflight(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "topo2stl")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue((ROOT / manifest["skills"]).is_dir())
        for key in ("composerIcon", "logo"):
            self.assertTrue((ROOT / manifest["interface"][key]).is_file())
        for screenshot in manifest["interface"]["screenshots"]:
            self.assertTrue((ROOT / screenshot).is_file())

        result = run_script(PREFLIGHT, SKILL / "assets" / "project-config.yaml")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: project inputs are complete", result.stdout)
        self.assertIn("fore-aft-4g", result.stdout)

    def test_release_validator_passes_and_catches_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = yaml.safe_load((SKILL / "assets" / "project-config.yaml").read_text())
            config_path = root / "project-config.yaml"
            config_path.write_text(yaml.safe_dump(config, sort_keys=False))

            write_cube(root / "final.stl")
            (root / "fea-results.json").write_text("{}")
            (root / "final.gcode").write_text("; test slicer output\n")
            (root / "evidence.png").write_bytes(b"test-image")

            manifest = {
                "schema_version": 1,
                "project_config": "project-config.yaml",
                "revision": "test",
                "artifacts": {
                    "final_stl": "final.stl",
                    "fea_results": "fea-results.json",
                    "slicer_output": "final.gcode",
                },
                "results": {
                    "maximum_displacement_mm": 0.5,
                    "minimum_p99_directional_fos": 4.0,
                    "volume_error_percent": 0.25,
                },
                "visual_evidence": {
                    "load_map": "evidence.png",
                    "before": "evidence.png",
                    "after": "evidence.png",
                    "optimization_progress": [
                        {"stage": stage, "path": "evidence.png"}
                        for stage in ("full-density", "early", "middle", "converged")
                    ],
                    "fea_hotspots": [
                        {"load_case": case["id"], "path": "evidence.png"}
                        for case in config["loading"]["cases"]
                    ],
                    "slicer_preview": "evidence.png",
                },
            }
            manifest_path = root / "evidence-manifest.json"
            manifest_path.write_text(json.dumps(manifest))

            result = run_script(VALIDATE_RELEASE, manifest_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"watertight": true', result.stdout)
            self.assertIn("PASS: release contract", result.stdout)

            (root / "evidence.png").unlink()
            result = run_script(VALIDATE_RELEASE, manifest_path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing file", result.stderr)


if __name__ == "__main__":
    unittest.main()
