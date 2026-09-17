import shutil
from pathlib import Path

from porting_harness.select_files import select_files

from .reference_patterns import reference_patterns
from .strip_builder_reexports import strip_builder_reexports


def assemble_reference_implementation(
    *,
    derivation_directory: Path,
    output_directory: Path,
    source_language: str,
    include_typescript_tests: bool,
    include_python_tests: bool,
) -> tuple[Path, list[str], list[str]]:
    source_directory = derivation_directory / "source" / source_language
    if not source_directory.is_dir():
        raise ValueError(f"No derived source for language: {source_language}")
    included = {
        "typescript": include_typescript_tests,
        "python": include_python_tests,
    }
    shutil.rmtree(output_directory, ignore_errors=True)
    output_directory.mkdir(parents=True)
    (output_directory / "source").mkdir()
    patterns = reference_patterns(
        source_language=source_language,
        include_typescript_tests=include_typescript_tests,
        include_python_tests=include_python_tests,
    )
    selected = select_files(source=source_directory, patterns=patterns)
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
                derivation_directory / "tests" / language,
                output_directory / "tests" / language,
            )
    return output_directory, patterns, [path.as_posix() for path in selected]
