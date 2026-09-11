import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import src.Codebase as codebase_module
from src.Codebase import Codebase

EXCLUDE = ["__pycache__", "*_test.py"]
SOURCE = "x = 1\n\n# note\ny = 2\n"
REPORT = {"suite": "unit", "total": 4, "passed": 3, "failed": 1, "errors": 0, "skipped": 0}
ADAPTED_REPORT = {
    **REPORT,
    "passed": 4,
    "failed": 0,
    "adapt": {"rules_fired": ["state_add", "exception_eq"]},
}
COVERAGE_REPORT = {
    **ADAPTED_REPORT,
    "coverage": {
        "line_pct": 78.52,
        "branch_pct": 65.26,
        "covered_lines": 720,
        "total_lines": 917,
    },
}
BRANCHING = "def f(a):\n    if a:\n        return 1\n    return 2\n"
PLAIN = "def g():\n    return 1\n"
AST_REPORT = {
    "language": "python",
    "target": "/data/run/ported_implementation",
    "parsed_file_count": 2,
    "node_count": 20,
    "max_depth": 6,
    "function_count": 2,
    "mean_function_lines": 3.0,
    "max_function_lines": 4,
    "mean_cyclomatic": 1.5,
    "max_cyclomatic": 2,
}
EMBED_REPORT = {"language": "typescript", "dims": 1024, "files": ["a.ts"], "embedded": 0, "skipped": 1}
COMPARE_REPORT = {
    "mean_cosine_distance": 0.02,
    "mean_nearest_file_distance": 0.08,
    "chamfer_distance": 0.11,
    "chamfer_a_to_b": 0.09,
    "chamfer_b_to_a": 0.13,
    "file_count_a": 1,
    "file_count_b": 1,
}
DISTANCE_REPORT = {
    "language": "typescript",
    "token_levenshtein": 0.45,
    "token_levenshtein_raw": 0.57,
    "char_levenshtein": 0.53,
    "path_levenshtein": 0.61,
}
GIT_DIFF_REPORT = {
    "language": "typescript",
    "insertions": 180,
    "deletions": 120,
    "reference_lines": 600,
    "diff_ratio": 0.5,
    "similarity_pct": 76.19,
    "identical": 2,
    "modified": 7,
    "renamed": 1,
    "added": 3,
    "deleted": 4,
    "formatter_failures": [],
}
API_TARGET = {
    "cases": 500,
    "agree_with_reference": 450,
    "disagree_with_reference": 50,
    "target_p50_elapsed_ns": 310550.0,
}
API_FIXTURE_TARGET = {
    **API_TARGET,
    "cases": 453,
    "agree_with_reference": 453,
    "disagree_with_reference": 0,
    "target_p50_elapsed_ns": 285100.0,
}


def rung(name: str, input_len: int, add_ms: float) -> dict:
    def phase(ms: float) -> dict:
        return {"median": ms * 1e6, "p90": ms * 1.1e6, "min": ms * 0.9e6, "spread": 0.1}

    return {"rung": name, "input_len": input_len, "construct_ns": phase(0.5), "add_ns": phase(add_ms)}


API_LADDER_TARGET = {
    **API_TARGET,
    "cases": 22,
    "agree_with_reference": 22,
    "disagree_with_reference": 0,
    "timings": [rung("1-literal", 1, 1.0), rung("8-json-depth", 10, 2.0), rung("8-json-depth", 100, 20.0)],
    "reference_timings": [
        rung("1-literal", 1, 1.0),
        rung("8-json-depth", 10, 1.0),
        rung("8-json-depth", 100, 10.0),
    ],
}


def api_report(target: Path, entry: dict) -> str:
    return json.dumps({"language": "typescript", "cases": entry["cases"], "targets": {str(target): entry}})


def make_tree(root: Path) -> None:
    pkg = root / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "a.py").write_text(SOURCE)
    (pkg / "a_test.py").write_text("assert True\n")
    (pkg / "__pycache__").mkdir()
    (pkg / "__pycache__" / "a.cpython-314.pyc").write_bytes(b"\x00")


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    make_tree(tmp_path)
    return tmp_path


@pytest.fixture
def run(tmp_path: Path) -> dict:
    run_dir = tmp_path / "20260909T000000Z_abcdef12"
    make_tree(run_dir / "ported_implementation")
    return {
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "source_language": "python",
        "target_language": "typescript",
    }


@pytest.fixture
def reference(tmp_path: Path) -> Path:
    return tmp_path / "reference" / "typescript"


@pytest.fixture
def uncached(monkeypatch):
    for store in (
        codebase_module.test_runs_cache,
        codebase_module.exercise_api_cache,
        codebase_module.reference_diff_cache,
    ):
        monkeypatch.setattr(store, "read", False)
        monkeypatch.setattr(store, "write", False)


@pytest.fixture
def cached(monkeypatch, tmp_path):
    monkeypatch.setattr(
        codebase_module.test_runs_cache,
        "path",
        lambda suite, run_id, adapt=False, coverage=False, **kwargs: (
            tmp_path
            / "cache"
            / f"{suite}{'-adapt' if adapt else ''}{'-coverage' if coverage else ''}"
            / f"{run_id}.pkl"
        ),
    )


@pytest.fixture
def subprocess_module(uncached):
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.return_value = Mock(returncode=1, stdout=json.dumps(REPORT), stderr="")
        yield m


@pytest.fixture
def adapted_subprocess_module(uncached):
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.return_value = Mock(returncode=0, stdout=json.dumps(ADAPTED_REPORT), stderr="")
        yield m


@pytest.fixture
def coverage_subprocess_module(uncached):
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.return_value = Mock(returncode=0, stdout=json.dumps(COVERAGE_REPORT), stderr="")
        yield m


@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "a.py").write_text(BRANCHING)
    (pkg / "b.py").write_text(PLAIN)
    (pkg / "a_test.py").write_text(BRANCHING + PLAIN)
    return tmp_path


@pytest.fixture
def measure_ast_process():
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.return_value = Mock(returncode=0, stdout=json.dumps(AST_REPORT), stderr="")
        yield m


@pytest.fixture
def measure_embedding_process():
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.side_effect = [
            Mock(returncode=0, stdout=json.dumps(EMBED_REPORT), stderr=""),
            Mock(returncode=0, stdout=json.dumps(EMBED_REPORT), stderr=""),
            Mock(returncode=0, stdout=json.dumps(COMPARE_REPORT), stderr=""),
        ]
        yield m


@pytest.fixture
def code_distance_process():
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.return_value = Mock(returncode=0, stdout=json.dumps(DISTANCE_REPORT), stderr="")
        yield m


@pytest.fixture
def reference_diff_process(uncached):
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.return_value = Mock(returncode=0, stdout=json.dumps(GIT_DIFF_REPORT), stderr="")
        yield m


@pytest.fixture
def diff_cached(monkeypatch, tmp_path):
    monkeypatch.setattr(
        codebase_module.reference_diff_cache,
        "path",
        lambda reference, target, **kwargs: tmp_path / "diff" / f"{Path(target).name}.pkl",
    )


ENTRY_BY_CASE_FILE = {"fixtures.jsonl": API_FIXTURE_TARGET, "ladder.jsonl": API_LADDER_TARGET}


def respond_to_exercise_api(target: Path):
    def respond(argv, **kwargs):
        cases = Path(argv[argv.index("--cases") + 1]).name
        entry = ENTRY_BY_CASE_FILE.get(cases, API_TARGET)
        return Mock(returncode=0, stdout=api_report(target, entry), stderr="")

    return respond


@pytest.fixture
def exercise_api_process(uncached, run):
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.side_effect = respond_to_exercise_api(Path(run["run_dir"]) / "ported_implementation")
        yield m


@pytest.fixture
def api_cached(monkeypatch, tmp_path):
    monkeypatch.setattr(
        codebase_module.exercise_api_cache,
        "path",
        lambda case_set, run_id, **kwargs: tmp_path / "cache" / case_set / f"{run_id}.pkl",
    )


def describe_codebase():
    def it_stores_the_path_as_a_path(tree):
        assert Codebase(str(tree)).path == tree

    def it_has_no_run_for_a_bare_path(tree):
        assert Codebase(tree).run is None

    def it_lists_files_as_a_frame_of_path_ext_size(tree):
        files = Codebase(tree).files
        assert files.columns == ["path", "ext", "size"]
        assert files.height == 3

    def it_drops_files_matching_exclude(tree):
        assert Codebase(tree, exclude=EXCLUDE).files["path"].to_list() == ["pkg/a.py"]

    def it_counts_code_lines_over_included_files(tree):
        assert Codebase(tree, exclude=EXCLUDE).loc == 2

    def it_counts_included_files(tree):
        assert Codebase(tree, exclude=EXCLUDE).file_count == 1

    def it_counts_every_physical_line_including_blank_and_comment_lines(tree):
        assert Codebase(tree, exclude=EXCLUDE).lines == 4

    def it_counts_characters_over_included_files(tree):
        assert Codebase(tree, exclude=EXCLUDE).chars == len(SOURCE)


def describe_from_run():
    def it_derives_the_path_from_the_run_dir(run):
        assert Codebase.from_run(run).path == Path(run["run_dir"]) / "ported_implementation"

    def it_keeps_the_run_row(run):
        assert Codebase.from_run(run).run == run

    def it_applies_exclude(run):
        assert Codebase.from_run(run, exclude=EXCLUDE).loc == 2

    def it_sets_the_language_from_the_target_language(run):
        assert Codebase.from_run(run).language == "typescript"


def describe_pass_rates():
    def it_has_none_for_a_bare_path(tree):
        assert Codebase(tree).unit_pass_pct is None
        assert Codebase(tree).integration_pass_pct is None

    def it_reports_passed_over_total_as_a_percentage(run, subprocess_module):
        assert Codebase.from_run(run).unit_pass_pct == 75.0

    def it_runs_the_unit_suite_against_the_port_in_the_target_language(run, subprocess_module):
        Codebase.from_run(run).unit_pass_pct
        argv = subprocess_module.run.call_args.args[0]
        assert argv[-6:] == [
            "--language",
            "typescript",
            "--target",
            str(Path(run["run_dir"]) / "ported_implementation"),
            "--suite",
            "unit",
        ]

    def it_runs_the_integration_suite_for_the_integration_rate(run, subprocess_module):
        Codebase.from_run(run).integration_pass_pct
        argv = subprocess_module.run.call_args.args[0]
        assert argv[-2:] == ["--suite", "integration"]

    def it_runs_each_suite_once_and_serves_the_rest_from_the_cache(run, cached):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=1, stdout=json.dumps(REPORT), stderr="")
            first = Codebase.from_run(run).unit_pass_pct
            second = Codebase.from_run(run).unit_pass_pct
        assert (first, second) == (75.0, 75.0)
        assert m.run.call_count == 1

    def it_raises_when_the_tool_produced_no_report(run, uncached):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=1, stdout="", stderr="boom")
            with pytest.raises(RuntimeError, match="boom"):
                Codebase.from_run(run).unit_pass_pct


def describe_adapted_pass_rates():
    def it_has_none_for_a_bare_path(tree):
        assert Codebase(tree).adapted_unit_pass_pct is None
        assert Codebase(tree).adapted_integration_pass_pct is None
        assert Codebase(tree).adapt_rules is None

    def it_reports_passed_over_total_as_a_percentage(run, adapted_subprocess_module):
        assert Codebase.from_run(run).adapted_unit_pass_pct == 100.0

    def it_runs_the_unit_suite_with_adapt(run, adapted_subprocess_module):
        Codebase.from_run(run).adapted_unit_pass_pct
        argv = adapted_subprocess_module.run.call_args.args[0]
        assert argv[-7:] == [
            "--language",
            "typescript",
            "--target",
            str(Path(run["run_dir"]) / "ported_implementation"),
            "--suite",
            "unit",
            "--adapt",
        ]

    def it_runs_the_integration_suite_with_adapt_for_the_integration_rate(
        run, adapted_subprocess_module
    ):
        Codebase.from_run(run).adapted_integration_pass_pct
        argv = adapted_subprocess_module.run.call_args.args[0]
        assert argv[-3:] == ["--suite", "integration", "--adapt"]

    def it_never_passes_adapt_for_the_strict_rates(run, subprocess_module):
        Codebase.from_run(run).unit_pass_pct
        Codebase.from_run(run).integration_pass_pct
        for call in subprocess_module.run.call_args_list:
            assert "--adapt" not in call.args[0]

    def it_joins_the_unit_suites_fired_rules_with_commas(run, adapted_subprocess_module):
        assert Codebase.from_run(run).adapt_rules == "state_add,exception_eq"
        argv = adapted_subprocess_module.run.call_args.args[0]
        assert argv[-3:] == ["--suite", "unit", "--adapt"]

    def it_is_an_empty_string_when_no_rule_fired(run, adapted_subprocess_module):
        report = {**ADAPTED_REPORT, "adapt": {"rules_fired": []}}
        adapted_subprocess_module.run.return_value = Mock(
            returncode=0, stdout=json.dumps(report), stderr=""
        )
        assert Codebase.from_run(run).adapt_rules == ""

    def it_caches_adapted_runs_apart_from_strict_ones():
        strict = codebase_module.test_runs_cache.path("unit", "abc", language="python", target=None)
        adapted = codebase_module.test_runs_cache.path(
            "unit", "abc", language="python", target=None, adapt=True
        )
        assert str(strict).endswith("codebases/test-runs/unit/abc.pkl")
        assert str(adapted).endswith("codebases/test-runs/unit-adapt/abc.pkl")

    def it_runs_the_adapted_suite_once_and_shares_it_between_rate_and_rules(run, cached):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=0, stdout=json.dumps(ADAPTED_REPORT), stderr="")
            codebase = Codebase.from_run(run)
            values = (codebase.unit_pass_pct, codebase.adapted_unit_pass_pct, codebase.adapt_rules)
        assert values == (100.0, 100.0, "state_add,exception_eq")
        assert m.run.call_count == 2


def describe_coverage():
    def it_has_none_for_a_bare_path(tree):
        assert Codebase(tree).adapted_unit_coverage_pct is None
        assert Codebase(tree).adapted_integration_coverage_pct is None

    def it_reports_the_measured_line_percentage(run, coverage_subprocess_module):
        assert Codebase.from_run(run).adapted_integration_coverage_pct == 78.52

    def it_runs_the_integration_suite_with_adapt_and_coverage(run, coverage_subprocess_module):
        Codebase.from_run(run).adapted_integration_coverage_pct
        argv = coverage_subprocess_module.run.call_args.args[0]
        assert argv[-4:] == ["--suite", "integration", "--adapt", "--coverage"]

    def it_measures_the_unit_suite_the_same_way(run, coverage_subprocess_module):
        Codebase.from_run(run).adapted_unit_coverage_pct
        argv = coverage_subprocess_module.run.call_args.args[0]
        assert argv[-4:] == ["--suite", "unit", "--adapt", "--coverage"]

    def it_never_passes_coverage_for_the_pass_rates(run, adapted_subprocess_module):
        Codebase.from_run(run).adapted_integration_pass_pct
        Codebase.from_run(run).unit_pass_pct
        for call in adapted_subprocess_module.run.call_args_list:
            assert "--coverage" not in call.args[0]

    def it_caches_measured_runs_apart_from_unmeasured_ones():
        adapted = codebase_module.test_runs_cache.path(
            "integration", "abc", language="python", target=None, adapt=True
        )
        measured = codebase_module.test_runs_cache.path(
            "integration", "abc", language="python", target=None, adapt=True, coverage=True
        )
        assert str(adapted).endswith("codebases/test-runs/integration-adapt/abc.pkl")
        assert str(measured).endswith(
            "codebases/test-runs/integration-adapt-coverage/abc.pkl"
        )

    def it_runs_the_measured_suite_once_and_serves_the_rest_from_the_cache(run, cached):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=0, stdout=json.dumps(COVERAGE_REPORT), stderr="")
            codebase = Codebase.from_run(run)
            values = (
                codebase.adapted_integration_coverage_pct,
                codebase.adapted_integration_coverage_pct,
            )
        assert values == (78.52, 78.52)
        assert m.run.call_count == 1

    def describe_the_reference():
        def it_measures_a_run_less_codebase_given_a_run_id(tree, coverage_subprocess_module):
            codebase = Codebase(tree, language="python", run_id="reference-python")
            assert codebase.adapted_integration_coverage_pct == 78.52
            argv = coverage_subprocess_module.run.call_args.args[0]
            assert argv[argv.index("--language") + 1] == "python"
            assert argv[argv.index("--target") + 1] == str(tree)

        def it_stays_none_without_a_language(tree, coverage_subprocess_module):
            assert Codebase(tree, run_id="reference-python").adapted_integration_coverage_pct is None

        def it_caches_under_the_run_id_it_was_given(tree, cached, tmp_path):
            with patch("src.Codebase.subprocess", autospec=True) as m:
                m.run.return_value = Mock(
                    returncode=0, stdout=json.dumps(COVERAGE_REPORT), stderr=""
                )
                Codebase(
                    tree, language="python", run_id="reference-python"
                ).adapted_integration_coverage_pct
            assert (
                tmp_path
                / "cache"
                / "integration-adapt-coverage"
                / "reference-python.pkl"
            ).exists()


def describe_ast_metrics():
    def it_has_no_language_for_a_bare_path(tree):
        assert Codebase(tree).language is None

    def it_takes_the_language_keyword(tree):
        assert Codebase(tree, EXCLUDE, language="python").language == "python"

    def it_has_none_for_every_metric_without_a_language(source_tree):
        codebase = Codebase(source_tree, exclude=EXCLUDE)
        assert codebase.node_count is None
        assert codebase.max_depth is None
        assert codebase.function_count is None
        assert codebase.mean_function_lines is None
        assert codebase.max_function_lines is None
        assert codebase.mean_cyclomatic is None
        assert codebase.max_cyclomatic is None

    def it_counts_named_nodes_and_depth_over_included_files(source_tree):
        codebase = Codebase(source_tree, exclude=EXCLUDE, language="python")
        assert (codebase.node_count, codebase.max_depth) == (20, 6)

    def it_counts_functions_over_included_files(source_tree):
        assert Codebase(source_tree, exclude=EXCLUDE, language="python").function_count == 2

    def it_reports_function_line_mean_and_max(source_tree):
        codebase = Codebase(source_tree, exclude=EXCLUDE, language="python")
        assert (codebase.mean_function_lines, codebase.max_function_lines) == (3.0, 4)

    def it_reports_cyclomatic_mean_and_max(source_tree):
        codebase = Codebase(source_tree, exclude=EXCLUDE, language="python")
        assert (codebase.mean_cyclomatic, codebase.max_cyclomatic) == (1.5, 2)

    def it_runs_measure_ast_with_language_target_and_each_exclude(source_tree, measure_ast_process):
        Codebase(source_tree, exclude=EXCLUDE, language="python").node_count
        argv = measure_ast_process.run.call_args.args[0]
        assert argv[argv.index("measure-ast"):] == [
            "measure-ast",
            "--language",
            "python",
            "--target",
            str(source_tree),
            "--exclude",
            "__pycache__",
            "--exclude",
            "*_test.py",
        ]

    def it_runs_measure_ast_once_for_all_seven_metrics(source_tree, measure_ast_process):
        codebase = Codebase(source_tree, exclude=EXCLUDE, language="python")
        values = [
            codebase.node_count,
            codebase.max_depth,
            codebase.function_count,
            codebase.mean_function_lines,
            codebase.max_function_lines,
            codebase.mean_cyclomatic,
            codebase.max_cyclomatic,
        ]
        assert values == [20, 6, 2, 3.0, 4, 1.5, 2]
        assert measure_ast_process.run.call_count == 1

    def it_raises_when_measure_ast_produced_no_report(source_tree, measure_ast_process):
        measure_ast_process.run.return_value = Mock(returncode=1, stdout="", stderr="boom")
        with pytest.raises(RuntimeError, match="boom"):
            Codebase(source_tree, exclude=EXCLUDE, language="python").node_count


def describe_embedding_distance():
    def it_has_none_without_a_reference(run):
        codebase = Codebase.from_run(run)
        assert codebase.embedding_distance is None
        assert codebase.embedding_nearest_file_distance is None
        assert codebase.chamfer_distance is None
        assert codebase.chamfer_a_to_b is None
        assert codebase.chamfer_b_to_a is None

    def it_has_none_for_a_bare_path(tree, reference):
        assert Codebase(tree, language="python", reference=reference).embedding_distance is None

    def it_reports_centroid_and_nearest_file_distance_to_the_reference(
        run, reference, measure_embedding_process
    ):
        codebase = Codebase.from_run(run, reference=reference)
        assert (codebase.embedding_distance, codebase.embedding_nearest_file_distance) == (0.02, 0.08)

    def it_reports_the_chamfer_distance_to_the_reference_in_both_directions(
        run, reference, measure_embedding_process
    ):
        codebase = Codebase.from_run(run, reference=reference)
        assert (codebase.chamfer_distance, codebase.chamfer_a_to_b, codebase.chamfer_b_to_a) == (0.11, 0.09, 0.13)

    def it_keeps_stripped_vectors_in_their_own_cache_directory():
        assert codebase_module.EMBEDDINGS.name == "embeddings-stripped"

    def it_embeds_the_port_and_the_reference_then_compares_them(
        run, reference, measure_embedding_process
    ):
        Codebase.from_run(run, exclude=EXCLUDE, reference=reference).embedding_distance
        calls = [call.args[0] for call in measure_embedding_process.run.call_args_list]
        target = str(Path(run["run_dir"]) / "ported_implementation")
        out = str(codebase_module.EMBEDDINGS / "runs" / run["run_id"])
        reference_out = str(codebase_module.EMBEDDINGS / "reference" / "typescript")
        excludes = ["--exclude", "__pycache__", "--exclude", "*_test.py"]
        model = ["--model", codebase_module.EMBEDDING_MODEL, "--strip-comments"]
        assert [argv[argv.index("measure-embedding") :] for argv in calls] == [
            ["measure-embedding", "embed", "--language", "typescript", "--target", target, "--out", out, *model, *excludes],
            ["measure-embedding", "embed", "--language", "typescript", "--target", str(reference), "--out", reference_out, *model, *excludes],
            ["measure-embedding", "compare", "--a", out, "--b", reference_out],
        ]

    def it_runs_measure_embedding_once_for_every_metric(run, reference, measure_embedding_process):
        codebase = Codebase.from_run(run, reference=reference)
        codebase.embedding_distance
        codebase.embedding_nearest_file_distance
        codebase.chamfer_distance
        codebase.chamfer_a_to_b
        codebase.chamfer_b_to_a
        assert measure_embedding_process.run.call_count == 3

    def it_raises_when_measure_embedding_produced_no_report(run, reference):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=1, stdout="", stderr="boom")
            with pytest.raises(RuntimeError, match="boom"):
                Codebase.from_run(run, reference=reference).embedding_distance


def describe_code_distance():
    def it_has_none_without_a_reference(run):
        codebase = Codebase.from_run(run)
        assert codebase.token_levenshtein is None
        assert codebase.char_levenshtein is None
        assert codebase.path_levenshtein is None

    def it_reports_token_char_and_path_levenshtein_to_the_reference(run, reference, code_distance_process):
        codebase = Codebase.from_run(run, reference=reference)
        assert (codebase.token_levenshtein, codebase.char_levenshtein, codebase.path_levenshtein) == (0.45, 0.53, 0.61)

    def it_runs_measure_code_distance_from_the_reference_to_the_port_with_each_exclude(
        run, reference, code_distance_process
    ):
        Codebase.from_run(run, exclude=EXCLUDE, reference=reference).token_levenshtein
        argv = code_distance_process.run.call_args.args[0]
        assert argv[argv.index("measure-code-distance") :] == [
            "measure-code-distance",
            "levenshtein",
            "--language",
            "typescript",
            "--a",
            str(reference),
            "--b",
            str(Path(run["run_dir"]) / "ported_implementation"),
            "--exclude",
            "__pycache__",
            "--exclude",
            "*_test.py",
        ]

    def it_runs_measure_code_distance_once_for_all_three_metrics(run, reference, code_distance_process):
        codebase = Codebase.from_run(run, reference=reference)
        codebase.token_levenshtein
        codebase.char_levenshtein
        codebase.path_levenshtein
        assert code_distance_process.run.call_count == 1

    def it_raises_when_measure_code_distance_produced_no_report(run, reference, code_distance_process):
        code_distance_process.run.return_value = Mock(returncode=1, stdout="", stderr="boom")
        with pytest.raises(RuntimeError, match="boom"):
            Codebase.from_run(run, reference=reference).char_levenshtein


def describe_reference_diff():
    def it_has_none_without_a_reference(run):
        codebase = Codebase.from_run(run)
        assert codebase.reference_diff_ratio is None
        assert codebase.reference_diff_identical is None
        assert codebase.reference_diff_similarity_pct is None

    def it_reports_the_diff_ratio_to_the_reference(run, reference, reference_diff_process):
        assert Codebase.from_run(run, reference=reference).reference_diff_ratio == 0.5

    def it_reports_every_file_count(run, reference, reference_diff_process):
        codebase = Codebase.from_run(run, reference=reference)
        counts = (
            codebase.reference_diff_identical,
            codebase.reference_diff_modified,
            codebase.reference_diff_renamed,
            codebase.reference_diff_added,
            codebase.reference_diff_deleted,
        )
        assert counts == (2, 7, 1, 3, 4)

    def it_measures_a_bare_path_that_has_a_reference(tree, reference, reference_diff_process):
        codebase = Codebase(tree, language="python", reference=reference)
        assert codebase.reference_diff_ratio == 0.5

    def it_runs_git_diff_from_the_reference_to_the_port_with_each_exclude(
        run, reference, reference_diff_process
    ):
        Codebase.from_run(run, exclude=EXCLUDE, reference=reference).reference_diff_ratio
        argv = reference_diff_process.run.call_args.args[0]
        assert argv[argv.index("measure-code-distance") :] == [
            "measure-code-distance",
            "git-diff",
            "--language",
            "typescript",
            "--a",
            str(reference),
            "--b",
            str(Path(run["run_dir"]) / "ported_implementation"),
            "--exclude",
            "__pycache__",
            "--exclude",
            "*_test.py",
        ]

    def it_runs_measure_code_distance_once_for_every_metric(run, reference, reference_diff_process):
        codebase = Codebase.from_run(run, reference=reference)
        codebase.reference_diff_ratio
        codebase.reference_diff_identical
        codebase.reference_diff_deleted
        assert reference_diff_process.run.call_count == 1

    def it_raises_when_git_diff_produced_no_report(run, reference, reference_diff_process):
        reference_diff_process.run.return_value = Mock(returncode=1, stdout="", stderr="boom")
        with pytest.raises(RuntimeError, match="boom"):
            Codebase.from_run(run, reference=reference).reference_diff_ratio

    def it_reports_the_percentage_of_reference_lines_the_diff_leaves_alone(
        run, reference, reference_diff_process
    ):
        assert Codebase.from_run(run, reference=reference).reference_diff_kept_pct == 80.0

    def it_reports_the_line_similarity_as_a_percentage(run, reference, reference_diff_process):
        codebase = Codebase.from_run(run, reference=reference)
        assert codebase.reference_diff_similarity_pct == 76.19

    def it_has_no_kept_percentage_without_a_reference(run):
        assert Codebase.from_run(run).reference_diff_kept_pct is None

    def it_has_no_kept_percentage_when_the_reference_has_no_lines(
        run, reference, reference_diff_process
    ):
        report = {**GIT_DIFF_REPORT, "reference_lines": 0, "deletions": 0, "diff_ratio": None}
        reference_diff_process.run.return_value = Mock(
            returncode=0, stdout=json.dumps(report), stderr=""
        )
        assert Codebase.from_run(run, reference=reference).reference_diff_kept_pct is None

    def it_caches_every_reference_and_port_pair_apart():
        pairs = (("/ref/one", "/port/one"), ("/ref/two", "/port/one"), ("/ref/one", "/port/two"))
        paths = {codebase_module.reference_diff_cache.path(Path(a), Path(b)) for a, b in pairs}
        assert len(paths) == 3

    def it_gives_the_same_pair_the_same_cache_file():
        pair = (Path("/ref/one"), Path("/port/one"))
        path = codebase_module.reference_diff_cache.path(*pair)
        assert path == codebase_module.reference_diff_cache.path(*pair)
        assert "codebases/reference-diff/" in str(path)
        assert str(path).endswith(".pkl")

    def it_runs_git_diff_once_for_a_pair_and_serves_the_rest_from_the_cache(
        run, reference, diff_cached
    ):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=0, stdout=json.dumps(GIT_DIFF_REPORT), stderr="")
            first = Codebase.from_run(run, reference=reference).reference_diff_kept_pct
            second = Codebase.from_run(run, reference=reference).reference_diff_ratio
        assert (first, second) == (80.0, 0.5)
        assert m.run.call_count == 1


def describe_api_agreement():
    def it_has_none_without_a_reference(run):
        codebase = Codebase.from_run(run)
        assert codebase.api_agreement_pct is None
        assert codebase.api_fixture_agreement_pct is None
        assert codebase.api_p50_ms is None

    def it_has_none_for_a_bare_path(tree, reference):
        assert Codebase(tree, language="python", reference=reference).api_agreement_pct is None

    def it_reports_agreeing_generated_cases_over_all_cases_as_a_percentage(
        run, reference, exercise_api_process
    ):
        assert Codebase.from_run(run, reference=reference).api_agreement_pct == 90.0

    def it_reports_fixture_agreement_from_the_fixture_cases(run, reference, exercise_api_process):
        assert Codebase.from_run(run, reference=reference).api_fixture_agreement_pct == 100.0

    def it_reports_the_generated_p50_in_milliseconds(run, reference, exercise_api_process):
        assert Codebase.from_run(run, reference=reference).api_p50_ms == 0.31055

    def it_runs_exercise_api_against_the_reference_with_the_generated_cases_and_adapt(
        run, reference, exercise_api_process
    ):
        Codebase.from_run(run, reference=reference).api_agreement_pct
        argv = exercise_api_process.run.call_args.args[0]
        assert argv[argv.index("exercise-api") :] == [
            "exercise-api",
            "--language",
            "typescript",
            "--reference",
            str(reference),
            "--target",
            str(Path(run["run_dir"]) / "ported_implementation"),
            "--cases",
            str(codebase_module.CASES["generated"]),
            "--adapt",
        ]

    def it_runs_the_fixture_cases_for_the_fixture_rate(run, reference, exercise_api_process):
        Codebase.from_run(run, reference=reference).api_fixture_agreement_pct
        argv = exercise_api_process.run.call_args.args[0]
        assert argv[-3:] == ["--cases", str(codebase_module.CASES["fixtures"]), "--adapt"]

    def it_ships_the_case_files_in_the_exercise_api_package():
        for path in codebase_module.CASES.values():
            assert path.is_file()

    def it_caches_each_case_set_apart():
        generated = codebase_module.exercise_api_cache.path("generated", "abc")
        fixtures = codebase_module.exercise_api_cache.path("fixtures", "abc")
        assert str(generated).endswith("codebases/exercise-api/generated/abc.pkl")
        assert str(fixtures).endswith("codebases/exercise-api/fixtures/abc.pkl")

    def it_runs_each_case_set_once_and_shares_it_between_agreement_and_p50(run, reference, api_cached):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.side_effect = respond_to_exercise_api(Path(run["run_dir"]) / "ported_implementation")
            codebase = Codebase.from_run(run, reference=reference)
            values = (codebase.api_agreement_pct, codebase.api_fixture_agreement_pct, codebase.api_p50_ms)
        assert values == (90.0, 100.0, 0.31055)
        assert m.run.call_count == 2

    def it_raises_when_exercise_api_produced_no_report(run, reference, uncached):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=1, stdout="", stderr="boom")
            with pytest.raises(RuntimeError, match="boom"):
                Codebase.from_run(run, reference=reference).api_agreement_pct


def describe_performance_ladder():
    def it_has_none_without_a_reference(run):
        codebase = Codebase.from_run(run)
        assert codebase.ladder_median_ms is None
        assert codebase.ladder_slope is None
        assert codebase.ladder_reference_slope is None
        assert codebase.ladder_ref_ratio is None
        assert codebase.ladder_timings is None
        assert codebase.ladder_rungs is None
        assert codebase.ladder_total_ms is None
        assert codebase.ladder_rungs_completed is None

    def it_takes_the_median_of_the_per_rung_add_medians(run, reference, exercise_api_process):
        assert Codebase.from_run(run, reference=reference).ladder_median_ms == 2.0

    def it_fits_the_log_log_slope_over_the_deepest_rung(run, reference, exercise_api_process):
        assert Codebase.from_run(run, reference=reference).ladder_slope == 1.0

    def it_divides_the_ports_median_by_the_references(run, reference, exercise_api_process):
        assert Codebase.from_run(run, reference=reference).ladder_ref_ratio == 2.0

    def it_fits_the_same_slope_over_the_references_own_rungs(run, reference, uncached):
        entry = {
            **API_LADDER_TARGET,
            "reference_timings": [
                rung("1-literal", 1, 1.0),
                rung("8-json-depth", 10, 1.0),
                rung("8-json-depth", 100, 100.0),
            ],
        }
        with patch("src.Codebase.subprocess", autospec=True) as m:
            target = Path(run["run_dir"]) / "ported_implementation"
            m.run.return_value = Mock(returncode=0, stdout=api_report(target, entry), stderr="")
            codebase = Codebase.from_run(run, reference=reference)
            assert codebase.ladder_slope == 1.0
            assert codebase.ladder_reference_slope == 2.0

    def it_exposes_the_per_rung_timings_for_the_chart(run, reference, exercise_api_process):
        codebase = Codebase.from_run(run, reference=reference)
        assert [entry["rung"] for entry in codebase.ladder_timings] == [
            "1-literal",
            "8-json-depth",
            "8-json-depth",
        ]
        assert len(codebase.ladder_reference_timings) == 3

    def it_exposes_each_rung_as_index_rung_input_len_and_ms(run, reference, exercise_api_process):
        codebase = Codebase.from_run(run, reference=reference)
        assert codebase.ladder_rungs[0] == {"index": 0, "rung": "1-literal", "input_len": 1, "ms": 1.0}
        assert [entry["ms"] for entry in codebase.ladder_rungs] == [1.0, 2.0, 20.0]
        assert [entry["ms"] for entry in codebase.ladder_reference_rungs] == [1.0, 1.0, 10.0]

    def it_numbers_each_rung_by_its_place_in_the_ladder_case_file(run, reference, uncached):
        cases = [json.loads(line) for line in codebase_module.CASES["ladder"].read_text().splitlines()]
        picked = [cases[0], cases[4], cases[21]]
        entry = {
            **API_LADDER_TARGET,
            "timings": [rung(case["rung"], len(case["input"]), 1.0) for case in picked],
        }
        with patch("src.Codebase.subprocess", autospec=True) as m:
            target = Path(run["run_dir"]) / "ported_implementation"
            m.run.return_value = Mock(returncode=0, stdout=api_report(target, entry), stderr="")
            codebase = Codebase.from_run(run, reference=reference)
            assert [entry["index"] for entry in codebase.ladder_rungs] == [0, 4, 21]

    def it_totals_the_per_rung_medians_over_the_rungs_that_completed(run, reference, exercise_api_process):
        codebase = Codebase.from_run(run, reference=reference)
        assert codebase.ladder_total_ms == 23.0
        assert codebase.ladder_reference_total_ms == 12.0
        assert codebase.ladder_rungs_completed == 3

    def it_has_none_when_every_rung_failed(run, reference, uncached):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            target = Path(run["run_dir"]) / "ported_implementation"
            entry = {**API_LADDER_TARGET, "timings": []}
            m.run.return_value = Mock(returncode=0, stdout=api_report(target, entry), stderr="")
            codebase = Codebase.from_run(run, reference=reference)
            assert codebase.ladder_median_ms is None
            assert codebase.ladder_ref_ratio is None
            assert codebase.ladder_total_ms is None
            assert codebase.ladder_rungs == []
            assert codebase.ladder_rungs_completed == 0

    def it_has_none_when_the_driver_failed_before_any_timing(run, reference, uncached):
        with patch("src.Codebase.subprocess", autospec=True) as m:
            target = Path(run["run_dir"]) / "ported_implementation"
            entry = {key: value for key, value in API_LADDER_TARGET.items() if key != "timings"}
            m.run.return_value = Mock(returncode=0, stdout=api_report(target, entry), stderr="")
            codebase = Codebase.from_run(run, reference=reference)
            assert codebase.ladder_timings is None
            assert codebase.ladder_median_ms is None
            assert codebase.ladder_slope is None
            assert codebase.ladder_ref_ratio is None
            assert codebase.ladder_rungs is None
            assert codebase.ladder_total_ms is None
            assert codebase.ladder_rungs_completed is None

    def it_takes_the_repeat_budget_from_the_ladder_case_file_not_a_flag(run, reference, exercise_api_process):
        codebase = Codebase.from_run(run, reference=reference)
        codebase.ladder_median_ms
        argv = exercise_api_process.run.call_args.args[0]
        assert argv[argv.index("--cases") :] == [
            "--cases",
            str(codebase_module.CASES["ladder"]),
            "--adapt",
        ]
        assert "--repeat" not in argv
        cases = [json.loads(line) for line in codebase_module.CASES["ladder"].read_text().splitlines()]
        assert all({"repeat", "warmup"} <= set(case) for case in cases)

    def it_caches_the_ladder_apart_from_the_other_case_sets():
        assert codebase_module.CASES["ladder"].name == "ladder.jsonl"
        assert str(codebase_module.exercise_api_cache.path("ladder", "abc")).endswith(
            "codebases/exercise-api/ladder/abc.pkl"
        )
