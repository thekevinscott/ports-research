from itertools import zip_longest

from measure_api.same_step import same_step


def classify_case(reference: dict, port: dict) -> tuple[str, int | None]:
    if reference["crash"] is not None or port["crash"] is not None:
        return "crash", None
    for index, (expected, actual) in enumerate(zip_longest(reference["steps"], port["steps"])):
        if not same_step(expected, actual):
            both_returned = expected is not None and actual is not None and "rules" in expected and "rules" in actual
            return ("mismatch" if both_returned else "error_mismatch"), index
    return ("error_match" if any("error" in step for step in reference["steps"]) else "match"), None
