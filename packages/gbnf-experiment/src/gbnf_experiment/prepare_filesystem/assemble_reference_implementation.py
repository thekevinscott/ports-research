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
    include_typescript_tests: bool,
    include_python_tests: bool,
) -> Path:
    source_directory = prepared_directory / "source" / source_language
    included = {
        "typescript": include_typescript_tests,
        "python": include_python_tests,
    }
    shutil.rmtree(output_directory, ignore_errors=True)
    output_directory.mkdir(parents=True)
    (output_directory / "source").mkdir()
    for relative in files:
        copy_file(source_directory / relative, output_directory / "source" / relative)
    (output_directory / "tests").mkdir()
    for language, wanted in included.items():
        if wanted:
            shutil.copytree(
                prepared_directory / "tests" / language,
                output_directory / "tests" / language,
            )
    return output_directory
