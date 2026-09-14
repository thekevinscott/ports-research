from gbnf_experiment.run_gbnf_experiment import TARGET_LANGUAGES


def reverse_condition(forward_condition: dict) -> dict:
    """The port becomes the source and goes back to the language it came from. Both suites
    ride along on every leg whatever the forward cell included, so reverse output measures
    the forward port rather than the reverse arm.
    """
    return {
        "source_language": TARGET_LANGUAGES[forward_condition["source_language"]],
        "include_typescript_tests": True,
        "include_python_tests": True,
        "effort": forward_condition["effort"],
        "model": forward_condition["model"],
    }
