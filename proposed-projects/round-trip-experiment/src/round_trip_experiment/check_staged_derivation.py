from pathlib import Path

TEST_SUITE_LANGUAGES = ("python", "typescript")


def check_staged_derivation(staged_derivation: Path, *, condition: dict) -> None:
    """PreparedFilesystem treats an absent cache-key directory as a cache miss and derives
    the real reference into it: a twenty-minute docker build against the wrong input. A stage
    that did not finish has to stop the leg before the harness is launched.
    """
    required = [
        staged_derivation / "source" / condition["source_language"],
        *(
            staged_derivation / "tests" / language
            for language in TEST_SUITE_LANGUAGES
            if condition[f"include_{language}_tests"]
        ),
    ]
    incomplete = [path for path in required if not path.is_dir() or not any(path.iterdir())]
    if incomplete:
        raise ValueError(
            "staged derivation is incomplete, refusing to launch: "
            + ", ".join(str(path) for path in incomplete)
        )
