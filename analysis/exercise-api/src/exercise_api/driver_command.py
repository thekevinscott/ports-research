import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
TSX_VERSION = "4.19.2"


def driver_command(*, language: str, target: Path, adapt: bool, repeat: int = 1, warmup: int = 0) -> list[str]:
    runner = {
        "python": [sys.executable, str(SCRIPTS / "driver.py")],
        "typescript": ["pnpm", "dlx", f"tsx@{TSX_VERSION}", str(SCRIPTS / "driver.ts")],
    }[language]
    return [
        *runner,
        "--target",
        str(target),
        *(["--adapt"] if adapt else []),
        *(["--repeat", str(repeat)] if repeat != 1 else []),
        *(["--warmup", str(warmup)] if warmup else []),
    ]
