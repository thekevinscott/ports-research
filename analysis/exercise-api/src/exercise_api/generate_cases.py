from hypothesis import HealthCheck, Phase, given, seed, settings

from .case_strategy import case_strategy

ROUNDS = 20
# Every round opens with hypothesis's simplest example, which is a duplicate after round one.
MINIMUM_ROUND = 10


def generate_cases(*, seed: int, count: int) -> list[dict]:
    cases: dict[tuple[str, str], dict] = {}
    for round_ in range(ROUNDS):
        if len(cases) >= count:
            break
        _collect(seed * ROUNDS + round_, max(2 * (count - len(cases)), MINIMUM_ROUND), cases)
    return list(cases.values())[:count]


def _collect(round_seed: int, wanted: int, cases: dict) -> None:
    @seed(round_seed)
    @settings(
        max_examples=wanted,
        database=None,
        phases=[Phase.generate],
        suppress_health_check=list(HealthCheck),
        deadline=None,
        derandomize=False,
    )
    @given(case_strategy())
    def collect(case):
        cases.setdefault((case["grammar"], case["input"]), case)

    collect()
