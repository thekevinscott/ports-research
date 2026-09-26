import json


def outcome_key(result: dict) -> str:
    rules = result["rules"]
    return json.dumps(
        {
            "ok": result["ok"],
            "error_type": result["error_type"],
            "error_pos": result["error_pos"],
            "rules": None if rules is None else sorted(json.dumps(rule, sort_keys=True) for rule in rules),
        },
        sort_keys=True,
    )
