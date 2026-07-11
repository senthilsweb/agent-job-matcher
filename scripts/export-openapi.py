#!/usr/bin/env python3
"""
File Name: export-openapi.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Export the backend's OpenAPI document as release artifacts — see
openspec/changes/add-openapi-release-artifact/.

This script produces the artifacts by:
1. Importing the FastAPI app (job_matcher.api) WITHOUT binding a port —
   FastAPI's native generator is the single source of truth; all
   metadata/examples live in the app definition itself.
2. Writing openapi.json and openapi.yaml into the output directory
   (default: dist/).
3. Exiting 0 with a clear notice while job_matcher.api does not exist
   yet (pre-Bolt-4), so the release workflow stays green before the API
   lands and activates automatically after.

Requirements:
- job-matcher (installed, e.g. pip install -e backend)
- pyyaml (optional — yaml output is skipped without it)

Environment Variables (.env at repo root):
- (none)
"""

# Import necessary libraries
import json
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    out_dir = Path(argv[1]) if len(argv) > 1 else Path("dist")

    # The API arrives with add-job-matcher-cli Bolt 4 — skip gracefully until then
    try:
        from job_matcher.api import app  # type: ignore[import-not-found]
    except ImportError as exc:
        print(f"NOTICE: job_matcher.api not present yet ({exc}) — skipping OpenAPI export.")
        return 0

    spec = app.openapi()
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "openapi.json"
    json_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {json_path}")

    try:
        import yaml

        yaml_path = out_dir / "openapi.yaml"
        yaml_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
        print(f"wrote {yaml_path}")
    except ImportError:
        print("NOTICE: pyyaml not installed — skipped openapi.yaml.")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
