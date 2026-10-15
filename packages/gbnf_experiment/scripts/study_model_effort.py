"""The model and effort study: four models at every effort level, unit and source integration tests, both directions.

40 cells a round, 12 rounds, 480 runs. Flags and stop rules are study.py's.
"""

from itertools import product

import study
from study import SOURCE_LANGUAGES

STUDY = "v2-model-effort"
MODELS = ("claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
TESTS = {
    "include_unit_tests": True,
    "include_source_integration_tests": True,
    "include_target_integration_tests": False,
}


def cells() -> list[dict]:
    return [
        {"source_language": source_language, **TESTS, "model": model, "effort": effort}
        for source_language, model, effort in product(SOURCE_LANGUAGES, MODELS, EFFORTS)
    ]


def main(argv: list[str] | None = None) -> None:
    study.main(STUDY, cells(), study.argument_parser(__doc__).parse_args(argv))


if __name__ == "__main__":
    main()
