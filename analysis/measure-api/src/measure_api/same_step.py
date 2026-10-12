from measure_api.rule_set import rule_set


def same_step(reference: dict | None, port: dict | None) -> bool:
    if reference is None or port is None or reference["step"] != port["step"]:
        return False
    if "rules" in reference and "rules" in port:
        return rule_set(reference["rules"]) == rule_set(port["rules"])
    if "error" in reference and "error" in port:
        expected, actual = reference["error"], port["error"]
        # A position counts only where the reference exposes one.
        return expected["class"] == actual["class"] and expected["pos"] in (None, actual["pos"])
    return False
