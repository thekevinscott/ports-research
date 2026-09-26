import shutil
from pathlib import Path


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def assemble_reference_implementation(*, source: Path, output: Path, files: list[str]) -> Path:
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True)
    for relative in files:
        copy_file(source / relative, output / relative)
    return output
