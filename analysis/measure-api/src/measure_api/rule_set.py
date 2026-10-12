import json


def rule_set(rules: list[dict]) -> frozenset[str]:
    return frozenset(json.dumps(rule, sort_keys=True, ensure_ascii=False) for rule in rules)
