import shutil
from pathlib import Path


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def assemble_reference_implementation(
    *,
    prepared_directory: Path,
    output_directory: Path,
    source_language: str,
    files: list[Path],
    test_files: list[Path],
) -> Path:
    source_directory = prepared_directory / "source" / source_language
    shutil.rmtree(output_directory, ignore_errors=True)
    output_directory.mkdir(parents=True)
    (output_directory / "source").mkdir()
    for relative in files:
        copy_file(source_directory / relative, output_directory / "source" / relative)
    for relative in test_files:
        copy_file(prepared_directory / "tests" / relative, output_directory / "tests" / relative)
    return output_directory
