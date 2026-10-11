LABELS = {
    "include_unit_tests": "unit-tests",
    "include_source_integration_tests": "source-integration-tests",
    "include_target_integration_tests": "target-integration-tests",
}


def condition_name(*, source_language: str, effort: str, model: str, **tests: bool) -> str:
    suites = [label for key, label in LABELS.items() if tests[key]]
    return "_".join([f"source-{source_language}", *suites, f"effort-{effort}", f"model-{model}"])
