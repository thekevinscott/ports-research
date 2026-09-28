def condition_name(
    *,
    source_language: str,
    include_javascript_tests: bool,
    include_python_tests: bool,
    effort: str,
    model: str,
) -> str:
    parts = [f"source-{source_language}"]
    if include_javascript_tests:
        parts.append("javascript-tests")
    if include_python_tests:
        parts.append("python-tests")
    parts.append(f"effort-{effort}")
    parts.append(f"model-{model}")
    return "_".join(parts)
