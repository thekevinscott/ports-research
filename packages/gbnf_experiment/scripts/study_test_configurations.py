"""The test-configuration study: Opus 5.5 at medium effort, every combination of the three test suites, both directions.

16 cells a round, 12 rounds, 192 runs. Flags and stop rules are study.py's.
"""

from itertools import product

import study
from study import FLAGS, SOURCE_LANGUAGES

STUDY = "v2-test-configurations"
MODEL = "claude-opus-5-5"
EFFORT = "medium"


def cells() -> list[dict]:
    return [
        {"source_language": source_language, **dict(zip(FLAGS, flags)), "model": MODEL, "effort": EFFORT}
        for source_language, flags in product(SOURCE_LANGUAGES, product((False, True), repeat=len(FLAGS)))
    ]


def main(argv: list[str] | None = None) -> None:
    study.main(STUDY, cells(), study.argument_parser(__doc__).parse_args(argv))


if __name__ == "__main__":
    main()
