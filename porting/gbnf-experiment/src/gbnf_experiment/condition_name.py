def condition_name(
    *,
    source_language: str,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
    effort: str,
    model: str,
) -> str:
    parts = [f"source-{source_language}"]
    if include_unit_tests:
        parts.append("unit-tests")
    if include_source_integration_tests:
        parts.append("source-integration-tests")
    if include_target_integration_tests:
        parts.append("target-integration-tests")
    parts.append(f"effort-{effort}")
    parts.append(f"model-{model}")
    return "_".join(parts)
