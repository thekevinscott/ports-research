from pathlib import Path


def reverse_command(
    *,
    condition: dict,
    staged_derivations_directory: Path,
    reverse_run_root: Path,
    gbnf_experiment_directory: Path,
) -> dict:
    """Both roots the harness reads are env-backed, so the reverse leg is a plain
    run-gbnf-experiment invocation with its two directories moved.
    """
    flags = [
        flag
        for flag, wanted in (
            ("--include-typescript-tests", condition["include_typescript_tests"]),
            ("--include-python-tests", condition["include_python_tests"]),
        )
        if wanted
    ]
    return {
        "argv": [
            "uv", "run", "--directory", str(gbnf_experiment_directory), "run-gbnf-experiment",
            "--source-language", condition["source_language"],
            *flags,
            "--effort", condition["effort"],
            "--model", condition["model"],
        ],
        "env": {
            "GBNF_EXPERIMENT_DERIVATIONS_DIRECTORY": str(staged_derivations_directory),
            "GBNF_EXPERIMENT_DATA_DIRECTORY": str(reverse_run_root),
        },
    }
