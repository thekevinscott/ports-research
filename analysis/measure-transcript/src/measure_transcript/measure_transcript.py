import json
import posixpath
from pathlib import Path

from measure_transcript.absolute_paths import absolute_paths
from measure_transcript.classify_path import OTHER, classify_path
from measure_transcript.command_word import command_word
from measure_transcript.copy_targets import copy_targets
from measure_transcript.expand_glob import expand_glob
from measure_transcript.is_fetch import is_fetch
from measure_transcript.is_test_path import is_test_path
from measure_transcript.read_transcript import read_transcript
from measure_transcript.reader_paths import reader_paths
from measure_transcript.reading_order import reading_order
from measure_transcript.reference_path import reference_path
from measure_transcript.resolve_path import resolve_path
from measure_transcript.segment_runtime import segment_runtime
from measure_transcript.split_command import split_command
from measure_transcript.suite_class import suite_class
from measure_transcript.suite_runner import suite_runner
from measure_transcript.summary_counts import summary_counts
from measure_transcript.text_runtimes import text_runtimes

SEARCH_TOOLS = {"Glob", "Grep"}
WEB_TOOLS = {"WebFetch", "WebSearch"}


def measure_transcript(run: Path) -> dict:
    """Counts and quoted commands from one run's transcript. See the README for each field."""
    manifest = json.loads((run / "manifest.json").read_text())
    source_language = manifest["condition"]["source_language"]
    if source_language not in OTHER:
        raise ValueError(f"source_language must be python or javascript, not {source_language!r}")
    transcript = read_transcript(run)
    # What is mounted at /input, to expand globs and finds against.
    files = {f"/input/{path}" for path in manifest["reference_implementation"]["included"]}

    copies: dict[str, str] = {}
    directories = {"/target", "/tmp", "/input"}
    calls = {"Bash": 0, "Read": 0, "Write": 0, "Edit": 0, "search": 0}
    reads = {"source": 0, "source_tests": 0, "target_tests": 0, "port": 0, "other": 0}
    touched: set[str] = set()
    suite_runs, own_files, fetches, read_log = [], [], [], []
    port_writes = 0
    first_write, evidence = None, None

    def classify(path):
        return classify_path(path, source_language, copies)

    def read(path):
        # A copy is read as its origin.
        read_log.append((reference_path(path, copies), classify(path), port_writes))

    def wrote(path, turn, whole=True):
        # A file the agent writes whole is its own, even inside a copy of the reference.
        nonlocal first_write, port_writes
        if classify_path(path, source_language, {}) != "port":
            return
        port_writes += 1
        if whole:
            copies[path] = path
        first_write = first_write or turn
        if is_test_path(path) and classify(path) == "port" and path not in own_files:
            own_files.append(path)

    def names_both(text):
        classes = {classify(p) for p in absolute_paths(text)}
        return {"source", "port"} <= classes

    for call in transcript["calls"]:
        name, turn, tool_input = call["name"], call["turn"], call["input"]
        if name in SEARCH_TOOLS:
            calls["search"] += 1
            touched.add(classify(tool_input.get("path")))
        elif name in calls:
            calls[name] += 1
        if name in WEB_TOOLS:
            fetches.append({"turn": turn, "command": f"{name} {tool_input.get('url') or tool_input.get('query') or ''}".strip()})
        elif name == "Read":
            cls = classify(tool_input.get("file_path"))
            reads[cls] += 1
            touched.add(cls)
            if tool_input.get("file_path"):
                read(tool_input["file_path"])
        elif name in ("Write", "Edit"):
            path = tool_input.get("file_path") or ""
            touched.add(classify(path))
            wrote(path, turn, whole=name == "Write")
            content = tool_input.get("content") or ""
            if evidence is None and name == "Write" and (text_runtimes(content) >= {"python", "node"} or names_both(content)):
                evidence = {"turn": turn, "path": path}
        elif name == "Bash":
            command = tool_input.get("command") or ""
            parsed = split_command(command, call["cwd"], files)
            runtimes = set()
            runs = []
            read_classes = set()
            for body in parsed["heredocs"]:
                runtimes |= text_runtimes(body)
            scripts_name_both = any(names_both(body) for body in parsed["heredocs"])
            for segment in parsed["segments"]:
                words, cwd = segment["words"], segment["cwd"]
                i = command_word(words)
                program = posixpath.basename(words[i]) if i < len(words) else ""
                args = [w for w in words[i + 1:] if not w.startswith("-")]
                touched |= {classify(resolve_path(a, cwd)) for a in args}
                operands = reader_paths(program, words[i + 1:])
                if operands is not None:
                    # A glob names the reference files it matches, under the reference or a copy of it.
                    paths = list(dict.fromkeys(e for p in operands for e in expand_glob(reference_path(resolve_path(p, cwd), copies), files)))
                    read_classes |= {classify(p) for p in paths}
                    for path in paths:
                        read(path)
                for path in segment["writes"]:
                    wrote(path, turn)
                for destination, origin in copy_targets(words[i:], cwd, directories):
                    copies[destination] = reference_path(origin, copies)
                    if not copies[destination].startswith("/input/") and is_test_path(destination):
                        wrote(destination, turn)
                if program == "mkdir":
                    directories |= {resolve_path(a, cwd) for a in args}
                directories.add(cwd)
                if runtime := segment_runtime(words):
                    runtimes.add(runtime)
                    if program.startswith("python") or program == "node":
                        for flag in ("-c", "-e"):
                            if flag in words[i + 1:-1]:
                                script = words[words.index(flag, i + 1) + 1]
                                runtimes |= text_runtimes(script)
                                scripts_name_both = scripts_name_both or names_both(script)
                if is_fetch(words):
                    fetches.append({"turn": turn, "command": " ".join(words)})
                paths = suite_runner(words)
                if paths is not None:
                    targets = [resolve_path(p, cwd) for p in paths] or [cwd]
                    runs.append({
                        "turn": turn,
                        "command": " ".join(words),
                        "suite": suite_class(targets, source_language, copies, own_files),
                        "passed": None,
                        "failed": None,
                    })
                    touched.add(runs[-1]["suite"])
            for cls in read_classes:
                reads[cls] += 1
            summaries = summary_counts(call["result"])
            if len(summaries) == len(runs):
                for run_record, counts in zip(runs, summaries):
                    run_record.update(counts)
            suite_runs += runs
            if evidence is None and (runtimes >= {"python", "node"} or scripts_name_both):
                evidence = {"turn": turn, "command": command}

    last_counts = {}
    for record in suite_runs:
        if record["passed"] is not None:
            last_counts[record["suite"]] = {"passed": record["passed"], "failed": record["failed"]}

    usage = transcript["usage"]
    totals = [
        u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("output_tokens", 0)
        for u in usage
    ]
    return {
        "turns": len(usage),
        "bash_calls": calls["Bash"],
        "read_calls": calls["Read"],
        "write_calls": calls["Write"],
        "edit_calls": calls["Edit"],
        "search_calls": calls["search"],
        "read_source": reads["source"],
        "read_source_tests": reads["source_tests"],
        "read_target_tests": reads["target_tests"],
        "touched_source_tests": "source_tests" in touched,
        "touched_target_tests": "target_tests" in touched,
        "suite_runs": suite_runs,
        "suite_run_count": len(suite_runs),
        "last_suite_counts": last_counts,
        "own_tests_written": len(own_files),
        "own_test_files": own_files,
        "differential_script": evidence is not None,
        "differential_evidence": evidence,
        "fetch_attempts": len(fetches),
        "fetch_commands": fetches,
        "input_tokens": sum(u.get("input_tokens", 0) for u in usage),
        "output_tokens": sum(u.get("output_tokens", 0) for u in usage),
        "cache_read_tokens": sum(u.get("cache_read_input_tokens", 0) for u in usage),
        "cache_creation_tokens": sum(u.get("cache_creation_input_tokens", 0) for u in usage),
        "tokens_before_first_write": sum(totals[: first_write - 1]) if first_write else None,
        "tokens_after_first_write": sum(totals[first_write - 1:]) if first_write else None,
        "first_write_turn": first_write,
        "last_suite_run_turn": suite_runs[-1]["turn"] if suite_runs else None,
        **reading_order(read_log, port_writes, calls["search"], source_language),
    }
