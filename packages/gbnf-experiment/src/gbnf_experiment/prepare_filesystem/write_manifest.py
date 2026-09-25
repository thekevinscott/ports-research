import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from python_on_whales import docker

from ..config import settings

ISO8601_UTC = "%Y-%m-%dT%H:%M:%SZ"
MANIFEST_FILENAME = "manifest.json"


def write_manifest(
    run_directory: Path,
    *,
    timestamp: datetime,
    condition: dict,
    included: list[str],
    image: str,
    gbnf_commit: str,
    completed_at: datetime | None = None,
    error: str | None = None,
) -> None:
    git = ["git", "-C", str(settings.root_directory)]
    manifest = {
        "timestamp": timestamp.astimezone(UTC).strftime(ISO8601_UTC),
        "completed_at": completed_at.astimezone(UTC).strftime(ISO8601_UTC)
        if completed_at
        else None,
        **({"error": error} if error is not None else {}),
        "condition": condition,
        "derivation": {
            "gbnf_commit": gbnf_commit,
        },
        "reference_implementation": {"included": included},
        "sandbox": {
            "image_id": docker.image.inspect(image).id,
        },
        "harness": {
            "commit": subprocess.run(
                [*git, "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip(),
            "dirty": bool(
                subprocess.run(
                    [*git, "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip()
            ),
        },
    }
    (run_directory / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2) + "\n")
