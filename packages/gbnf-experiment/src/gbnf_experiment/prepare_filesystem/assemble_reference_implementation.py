import shutil
from collections.abc import Sequence
from pathlib import Path

from porting_harness.select_files import select_files

from .strip_builder_reexports import strip_builder_reexports


def assemble_reference_implementation(
    *,
    prepared_directory: Path,
    output_directory: Path,
    source_language: str,
    patterns: Sequence[str],
    include_typescript_tests: bool,
    include_python_tests: bool,
) -> Path:
    source_directory = prepared_directory / "source" / source_language
    if not source_directory.is_dir():
        raise ValueError(f"No prepared source for language: {source_language}")
    included = {
        "typescript": include_typescript_tests,
        "python": include_python_tests,
    }
    shutil.rmtree(output_directory, ignore_errors=True)
    output_directory.mkdir(parents=True)
    (output_directory / "source").mkdir()
    selected = select_files(source=source_directory, patterns=list(patterns))
    for relative in selected:
        target = output_directory / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_directory / relative, target)
    if source_language == "typescript":
        strip_builder_reexports(output_directory / "source" / "src" / "index.ts")
    (output_directory / "tests").mkdir()
    for language, wanted in included.items():
        if wanted:
            shutil.copytree(
                prepared_directory / "tests" / language,
                output_directory / "tests" / language,
            )
    return output_directory
