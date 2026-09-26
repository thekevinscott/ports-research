import argparse
import importlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

# Not a package module: a subprocess entry point run_driver shells out to with the
# port root on sys.path, mirroring execute-test-suite's PYTHONPATH strategy. Must
# stay stdlib-only; it runs inside whatever interpreter loads the port.

PHASES = ("construct_ns", "add_ns")
LOAD_ERROR = {"ok": False, "error_type": "LoadError", "error_pos": None, "rules": None, "elapsed_ns": None}
TYPE_NAMES = {
    "rulechar": "char",
    "char": "char",
    "rulecharexclude": "char_exclude",
    "charexclude": "char_exclude",
    "char_exclude": "char_exclude",
    "ruleend": "end",
    "end": "end",
}


def load(target: Path, adapt: bool):
    sys.path.insert(0, str(target))
    if adapt and (target / "gbnf.py").is_file() and not (target / "gbnf").is_dir():
        spec = importlib.util.spec_from_file_location(
            "gbnf", target / "__init__.py", submodule_search_locations=[str(target)]
        )
        package = importlib.util.module_from_spec(spec)
        sys.modules["gbnf"] = package
        spec.loader.exec_module(package)
    return importlib.import_module("gbnf").GBNF


def normalize_type(raw) -> str:
    raw = getattr(raw, "value", raw)
    name = str(raw).lower().replace("-", "_").removeprefix("ruletype.")
    return TYPE_NAMES.get(name) or TYPE_NAMES.get(name.replace("_", "")) or name


def normalize_value(value):
    if isinstance(value, (list, tuple)):
        return [normalize_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): normalize_value(v) for k, v in value.items()}
    return value


def normalize_rule(rule) -> dict:
    if isinstance(rule, dict):
        raw_type, has_value, value = rule.get("type"), "value" in rule, rule.get("value")
    else:
        raw_type = getattr(rule, "type", None) or type(rule).__name__
        has_value, value = hasattr(rule, "value"), getattr(rule, "value", None)
    normalized = {"type": normalize_type(raw_type)}
    if has_value:
        normalized["value"] = normalize_value(value)
    return normalized


def run_case(GBNF, case: dict) -> dict:
    start = time.perf_counter_ns()
    try:
        grammar = GBNF(case["grammar"])
        constructed = time.perf_counter_ns()
        state = grammar.add(case["input"])
        added = time.perf_counter_ns()
        rules = [normalize_rule(rule) for rule in state]
        return {
            "ok": True,
            "error_type": None,
            "error_pos": None,
            "rules": rules,
            "elapsed_ns": time.perf_counter_ns() - start,
            "construct_ns": constructed - start,
            "add_ns": added - constructed,
        }
    except Exception as e:
        pos = getattr(e, "pos", None)
        return {
            "ok": False,
            "error_type": type(e).__name__,
            "error_pos": pos if isinstance(pos, int) and not isinstance(pos, bool) else None,
            "rules": None,
            "elapsed_ns": time.perf_counter_ns() - start,
            "construct_ns": None,
            "add_ns": None,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--adapt", action="store_true")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=0)
    args = parser.parse_args()

    out = os.fdopen(os.dup(1), "w")
    sys.stdout = sys.stderr
    cases = [json.loads(line) for line in sys.stdin if line.strip()]

    try:
        GBNF = load(args.target, args.adapt)
    except Exception:
        GBNF = None
    if GBNF is None:
        for _ in cases:
            out.write(json.dumps(LOAD_ERROR) + "\n")
            out.flush()
        return

    # A case may carry its own budget: the timeout covers the whole list, so without one
    # the slowest case dictates how often every other case can be measured.
    budgets = [(case.get("warmup", args.warmup), max(case.get("repeat", args.repeat), 1)) for case in cases]
    samples = [{phase: [] for phase in PHASES} for _ in cases]
    results: list[dict] = [{} for _ in cases]
    for index in range(max((warmup + repeat for warmup, repeat in budgets), default=0)):
        for position, (case, (warmup, repeat)) in enumerate(zip(cases, budgets)):
            if index >= warmup + repeat:
                continue
            result = run_case(GBNF, case)
            phases = {phase: result.pop(phase) for phase in PHASES}
            if index >= warmup:
                for phase, value in phases.items():
                    samples[position][phase].append(value)
            results[position] = result
    for case, sample, result in zip(cases, samples, results):
        keep = args.repeat > 1 or "repeat" in case
        out.write(json.dumps({**result, **sample} if keep else result, default=repr) + "\n")
    out.flush()


if __name__ == "__main__":
    main()
