from pathlib import Path


def reverse_command(
    *,
    condition: dict,
    gbnf_experiment_directory: Path,
) -> dict:
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
            "uv", "run", "--directory", str(gbnf_experiment_directory), "run_gbnf_experiment",
            "--source-language", condition["source_language"],
            *flags,
            "--effort", condition["effort"],
            "--model", condition["model"],
        ],
    }
