import shutil
from pathlib import Path

from .remove_builder import remove_builder
from .remove_colocated_tests import remove_colocated_tests
from .remove_dev_harness import remove_dev_harness


def assemble_reference_implementation(
    *,
    derivation_directory: Path,
    output_directory: Path,
    source_language: str,
    include_typescript_tests: bool,
    include_python_tests: bool,
) -> Path:
    source_directory = derivation_directory / "source" / source_language
    if not source_directory.is_dir():
        raise ValueError(f"No derived source for language: {source_language}")
    included = {
        "typescript": include_typescript_tests,
        "python": include_python_tests,
    }
    shutil.rmtree(output_directory, ignore_errors=True)
    output_directory.mkdir(parents=True)
    shutil.copytree(source_directory, output_directory / "source")
    remove_colocated_tests(
        directory=output_directory / "source",
        languages=[language for language, wanted in included.items() if not wanted],
    )
    remove_dev_harness(
        directory=output_directory / "source",
        language=source_language,
    )
    remove_builder(
        directory=output_directory / "source",
        language=source_language,
    )
    (output_directory / "tests").mkdir()
    for language, wanted in included.items():
        if wanted:
            shutil.copytree(
                derivation_directory / "tests" / language,
                output_directory / "tests" / language,
            )
    return output_directory
