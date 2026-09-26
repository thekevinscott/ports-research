import json
from pathlib import Path

MANIFEST_FILENAME = "manifest.json"


def record_forward(reverse_run_directory: Path, *, run_id: str, condition: dict) -> dict:
    """write_manifest builds a closed literal with no passthrough, so the join back to the
    forward run is added by re-reading the file the harness just wrote. Its own keys and its
    formatting are left as they were.
    """
    manifest_path = reverse_run_directory / MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text())
    manifest["forward"] = {"run_id": run_id, "condition": condition}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
