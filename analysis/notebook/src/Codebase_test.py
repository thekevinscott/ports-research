import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import src.Codebase as codebase_module
from src.Codebase import Codebase, content_hash, transcript_hash

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
        codebase_module.reference_diff_cache,
        codebase_module.behavior_cache,
        codebase_module.api_cache,
        codebase_module.ast_cache,
        codebase_module.transcript_cache,
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


@pytest.fixture(autouse=True)
def embedding_server_key(monkeypatch):
    """A server matching the cache, without a server; the check is cached, so each test starts it afresh."""
    monkeypatch.setenv("GENERATE_EMBEDDING_BASE_URL", "http://host/v1")
    codebase_module.check_embedding_server.cache_clear()
    with patch("src.Codebase.embedding_server_key", return_value=codebase_module.EMBEDDING_SERVER) as m:
        yield m
    codebase_module.check_embedding_server.cache_clear()


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

    def it_keeps_stripped_vectors_in_their_own_cache_directory_per_model_file_and_pooling():
        assert codebase_module.EMBEDDINGS.parts[-2:] == ("embeddings-stripped", "qwen3-embedding-0.6b-q8_0-pooling-last")

    def it_refuses_to_embed_from_a_server_whose_model_file_or_pooling_differs(run, reference, embedding_server_key, measure_embedding_process):
        embedding_server_key.return_value = "qwen3-embedding-0.6b-f16-pooling-mean"
        with pytest.raises(RuntimeError, match="serves qwen3-embedding-0.6b-f16-pooling-mean"):
            Codebase.from_run(run, reference=reference).embedding_distance
        embedding_server_key.assert_called_once_with("http://host/v1", codebase_module.EMBEDDING_MODEL)
        measure_embedding_process.run.assert_not_called()

    def it_refuses_to_embed_without_a_server_url(run, reference, monkeypatch, measure_embedding_process):
        monkeypatch.delenv("GENERATE_EMBEDDING_BASE_URL")
        with pytest.raises(RuntimeError, match="GENERATE_EMBEDDING_BASE_URL"):
            Codebase.from_run(run, reference=reference).embedding_distance

    def it_embeds_the_port_and_the_reference_then_compares_them(
        run, reference, measure_embedding_process
    ):
        Codebase.from_run(run, exclude=EXCLUDE, reference=reference).embedding_distance
        calls = [call.args[0] for call in measure_embedding_process.run.call_args_list]
        target = str(Path(run["run_dir"]) / "ported_implementation")
        out = str(codebase_module.EMBEDDINGS / "runs" / run["run_id"])
        reference_out = str(codebase_module.EMBEDDINGS / "reference" / codebase_module.GBNF_COMMIT / "typescript")
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


OUTCOMES = ["accept", "reject", "error", "crash"]
REFERENCE_OUTCOMES = ["accept", "reject", "error", "accept"]


def read_jsonl(path: str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def outcome_lines(outcomes: list[str], error: str | None = None) -> str:
    return "".join(
        json.dumps({"grammar": "g0000", "input": i, "outcome": outcome, "error": error}) + "\n"
        for i, outcome in enumerate(outcomes)
    )


def respond_to_measure_behavior(port_outcomes: list[str], error: str | None = None):
    def respond(argv, **kwargs):
        out = Path(argv[argv.index("--out") + 1])
        if "compare" in argv:
            reference = read_jsonl(argv[argv.index("--reference") + 1])
            port = read_jsonl(argv[argv.index("--port") + 1])
            confusion = {a: {b: 0 for b in OUTCOMES} for a in OUTCOMES}
            for r, p in zip(reference, port):
                confusion[r["outcome"]][p["outcome"]] += 1
            agreements = sum(confusion[o][o] for o in OUTCOMES)
            report = {
                "pairs": len(reference),
                "agreements": agreements,
                "agreement_rate": agreements / len(reference),
                "confusion": confusion,
            }
            out.write_text(json.dumps(report))
        else:
            out.write_text(outcome_lines(port_outcomes, error))
        return Mock(returncode=0, stdout="", stderr="")

    return respond


def v2_run(tmp_path: Path, name: str, target: str) -> dict:
    run_dir = tmp_path / name
    (run_dir / "ported_implementation").mkdir(parents=True)
    return {
        "run_id": name,
        "run_dir": str(run_dir),
        "source_language": "javascript" if target == "python" else "python",
        "target_language": target,
    }


@pytest.fixture
def behavior_corpus(monkeypatch, tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for driver in ("python", "typescript"):
        (corpus / f"reference-{driver}.jsonl").write_text(outcome_lines(REFERENCE_OUTCOMES))
    monkeypatch.setattr(codebase_module, "BEHAVIOR_CORPUS", corpus)
    return corpus


@pytest.fixture
def python_port(tmp_path):
    run = v2_run(tmp_path, "20261012T000000Z_py000001", "python")
    package = Path(run["run_dir"]) / "ported_implementation" / "gbnf"
    package.mkdir()
    (package / "__init__.py").write_text("GBNF = None\n")
    return run


@pytest.fixture
def javascript_port(tmp_path):
    run = v2_run(tmp_path, "20261012T000000Z_js000001", "javascript")
    src = Path(run["run_dir"]) / "ported_implementation" / "src"
    src.mkdir()
    (src / "index.ts").write_text("export default {};\n")
    return run


@pytest.fixture
def behavior_process(uncached, behavior_corpus):
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.side_effect = respond_to_measure_behavior(["accept", "reject", "error", "reject"])
        yield m


@pytest.fixture
def behavior_cached(monkeypatch, tmp_path):
    monkeypatch.setattr(
        codebase_module.behavior_cache,
        "path",
        lambda contents, **kwargs: tmp_path / "behavior" / f"{contents}.pkl",
    )


def measure_behavior_argv(process, command: str) -> list[str]:
    for call in process.run.call_args_list:
        argv = call.args[0]
        if argv[argv.index("measure-behavior") + 1] == command:
            return argv[argv.index("measure-behavior") :]
    raise AssertionError(f"measure-behavior {command} never ran")


def describe_behavior():
    def it_reports_agreement_with_the_reference_as_a_percentage(python_port, behavior_process):
        assert Codebase.from_run(python_port).behavior_agreement_pct == 75.0

    def it_reports_the_confusion_counts_by_reference_and_port_outcome(
        python_port, behavior_process
    ):
        confusion = Codebase.from_run(python_port).behavior_confusion
        assert confusion["accept"] == {"accept": 1, "reject": 1, "error": 0, "crash": 0}
        assert confusion["error"]["error"] == 1

    def it_runs_a_python_port_against_the_held_out_corpus_with_the_python_driver(
        python_port, behavior_process, behavior_corpus
    ):
        Codebase.from_run(python_port).behavior_agreement_pct
        argv = measure_behavior_argv(behavior_process, "run")
        assert argv[:6] == [
            "measure-behavior",
            "run",
            "--corpus",
            str(behavior_corpus),
            "--implementation",
            str(Path(python_port["run_dir"]) / "ported_implementation"),
        ]
        assert argv[argv.index("--language") + 1] == "python"

    def it_runs_a_javascript_port_that_ships_src_index_ts_with_the_typescript_driver(
        javascript_port, behavior_process
    ):
        Codebase.from_run(javascript_port).behavior_agreement_pct
        argv = measure_behavior_argv(behavior_process, "run")
        assert argv[argv.index("--language") + 1] == "typescript"

    def it_compares_the_port_with_the_reference_outcomes_of_its_driver(
        javascript_port, behavior_process, behavior_corpus
    ):
        Codebase.from_run(javascript_port).behavior_agreement_pct
        argv = measure_behavior_argv(behavior_process, "compare")
        assert argv[argv.index("--reference") + 1] == str(
            behavior_corpus / "reference-typescript.jsonl"
        )

    def it_runs_measure_behavior_from_its_own_package(python_port, behavior_process):
        Codebase.from_run(python_port).behavior_agreement_pct
        argv = behavior_process.run.call_args.args[0]
        assert argv[:4] == ["uv", "run", "--directory", str(codebase_module.MEASURE_BEHAVIOR_DIR)]

    def it_gives_a_javascript_port_without_src_index_ts_zero_agreement_and_a_note(
        tmp_path, behavior_process
    ):
        run = v2_run(tmp_path, "20261012T000000Z_js000002", "javascript")
        (Path(run["run_dir"]) / "ported_implementation" / "index.js").write_text("")
        codebase = Codebase.from_run(run)
        assert codebase.behavior_agreement_pct == 0.0
        assert codebase.behavior_confusion["accept"]["crash"] == 2
        assert codebase.behavior_note == "every pair crashed: no src/index.ts"
        assert [call.args[0][5] for call in behavior_process.run.call_args_list] == ["compare"]

    def it_notes_the_first_error_when_every_pair_crashed(python_port, behavior_process):
        behavior_process.run.side_effect = respond_to_measure_behavior(
            ["crash"] * 4, "ModuleNotFoundError: No module named 'gbnf'"
        )
        codebase = Codebase.from_run(python_port)
        assert codebase.behavior_agreement_pct == 0.0
        assert codebase.behavior_note == (
            "every pair crashed: ModuleNotFoundError: No module named 'gbnf'"
        )

    def it_has_no_note_when_a_pair_ran(python_port, behavior_process):
        assert Codebase.from_run(python_port).behavior_note is None

    def it_runs_measure_behavior_once_for_every_column(python_port, behavior_process):
        codebase = Codebase.from_run(python_port)
        codebase.behavior_agreement_pct
        codebase.behavior_confusion
        codebase.behavior_note
        assert behavior_process.run.call_count == 2

    def it_raises_when_measure_behavior_fails(python_port, behavior_process):
        behavior_process.run.side_effect = None
        behavior_process.run.return_value = Mock(returncode=1, stdout="", stderr="boom")
        with pytest.raises(RuntimeError, match="boom"):
            Codebase.from_run(python_port).behavior_agreement_pct

    def it_serves_a_port_with_the_same_contents_from_the_cache(
        tmp_path, python_port, behavior_corpus, behavior_cached
    ):
        twin = v2_run(tmp_path, "20261012T000000Z_py000002", "python")
        shutil.copytree(
            Path(python_port["run_dir"]) / "ported_implementation",
            Path(twin["run_dir"]) / "ported_implementation",
            dirs_exist_ok=True,
        )
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.side_effect = respond_to_measure_behavior(["accept", "reject", "error", "reject"])
            first = Codebase.from_run(python_port).behavior_agreement_pct
            second = Codebase.from_run(twin).behavior_agreement_pct
        assert (first, second) == (75.0, 75.0)
        assert m.run.call_count == 2


def describe_content_hash():
    def it_matches_for_two_ports_with_the_same_files(tmp_path):
        make_tree(tmp_path / "a")
        make_tree(tmp_path / "b")
        assert content_hash(tmp_path / "a") == content_hash(tmp_path / "b")

    def it_changes_when_a_file_changes(tmp_path):
        make_tree(tmp_path / "a")
        before = content_hash(tmp_path / "a")
        (tmp_path / "a" / "pkg" / "a.py").write_text("x = 2\n")
        assert content_hash(tmp_path / "a") != before

    def it_changes_when_a_file_moves(tmp_path):
        make_tree(tmp_path / "a")
        before = content_hash(tmp_path / "a")
        (tmp_path / "a" / "pkg" / "a.py").rename(tmp_path / "a" / "pkg" / "b.py")
        assert content_hash(tmp_path / "a") != before

    def it_ignores_installed_dependencies_caches_and_dot_directories(tmp_path):
        make_tree(tmp_path / "a")
        before = content_hash(tmp_path / "a")
        for directory in ("node_modules/x", ".vite", "pkg/__pycache__"):
            (tmp_path / "a" / directory).mkdir(parents=True, exist_ok=True)
            (tmp_path / "a" / directory / "f").write_text("changed\n")
        assert content_hash(tmp_path / "a") == before

    def it_does_not_follow_a_symlink_back_into_the_port(tmp_path):
        make_tree(tmp_path / "a")
        (tmp_path / "a" / "pkg" / "loop").symlink_to(tmp_path / "a")
        assert len(content_hash(tmp_path / "a")) == 64


def describe_tool_directories():
    def it_points_every_tool_at_a_package_in_the_tree():
        directories = {
            name: value
            for name, value in vars(codebase_module).items()
            if name.endswith("_DIR") and isinstance(value, Path)
        }
        assert directories
        assert [name for name, path in directories.items() if not path.is_dir()] == []


def step(rules: list[dict] | None = None, error: str | None = None) -> dict:
    if error is not None:
        return {"step": "construct", "error": {"class": error, "pos": None}}
    return {"step": "construct", "rules": rules}


OK = [step([{"type": "RuleChar", "value": [97]}])]
OTHER = [step([{"type": "RuleChar", "value": [98]}])]
RAISES = [step(error="GrammarParseError")]
# The reference returns, returns, raises, returns; the port matches, differs, matches the
# raise and crashes: one case per outcome but error_mismatch.
REFERENCE_CASES = [(OK, None), (OK, None), (RAISES, None), (OK, None)]
PORT_CASES = [(OK, None), (OTHER, None), (RAISES, None), (None, "Traceback: boom")]


def case_lines(cases: list[tuple[list[dict] | None, str | None]]) -> str:
    return "".join(
        json.dumps({"grammar": "g0000", "input": i, "steps": steps, "crash": crash}) + "\n"
        for i, (steps, crash) in enumerate(cases)
    )


def api_status(case: dict) -> str:
    if case["crash"] is not None:
        return "crash"
    return "error" if any("error" in s for s in case["steps"]) else "ok"


def api_outcome(reference: dict, port: dict) -> str:
    if "crash" in (api_status(reference), api_status(port)):
        return "crash"
    if reference["steps"] == port["steps"]:
        return "error_match" if api_status(reference) == "error" else "match"
    return "mismatch" if api_status(reference) == api_status(port) == "ok" else "error_mismatch"


def respond_to_measure_api(port_cases: list[tuple[list[dict] | None, str | None]]):
    def respond(argv, **kwargs):
        out = Path(argv[argv.index("--out") + 1])
        if "compare" in argv:
            reference = read_jsonl(argv[argv.index("--reference") + 1])
            port = read_jsonl(argv[argv.index("--port") + 1])
            statuses = ["ok", "error", "crash"]
            outcomes = dict.fromkeys(["match", "mismatch", "error_match", "error_mismatch", "crash"], 0)
            confusion = {a: dict.fromkeys(statuses, 0) for a in statuses}
            for r, p in zip(reference, port):
                outcomes[api_outcome(r, p)] += 1
                confusion[api_status(r)][api_status(p)] += 1
            agreements = outcomes["match"] + outcomes["error_match"]
            report = {
                "cases": len(reference),
                "agreements": agreements,
                "agreement_rate": agreements / len(reference),
                "outcomes": outcomes,
                "confusion": confusion,
                "disagreements": [],
            }
            out.write_text(json.dumps(report))
        else:
            out.write_text(case_lines(port_cases))
        return Mock(returncode=0, stdout="", stderr="")

    return respond


@pytest.fixture
def api_corpus(monkeypatch, tmp_path):
    corpus = tmp_path / "api-corpus"
    corpus.mkdir()
    for driver in ("python", "typescript"):
        (corpus / f"reference-{driver}.jsonl").write_text(case_lines(REFERENCE_CASES))
    monkeypatch.setattr(codebase_module, "API_CORPUS", corpus)
    return corpus


@pytest.fixture
def api_process(uncached, api_corpus):
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.side_effect = respond_to_measure_api(PORT_CASES)
        yield m


@pytest.fixture
def api_cached(monkeypatch, tmp_path):
    monkeypatch.setattr(
        codebase_module.api_cache,
        "path",
        lambda contents, **kwargs: tmp_path / "api" / f"{contents}.pkl",
    )


def measure_api_argv(process, command: str) -> list[str]:
    for call in process.run.call_args_list:
        argv = call.args[0]
        if argv[argv.index("measure-api") + 1] == command:
            return argv[argv.index("measure-api") :]
    raise AssertionError(f"measure-api {command} never ran")


def describe_api():
    def it_reports_agreement_with_the_reference_as_a_percentage(python_port, api_process):
        assert Codebase.from_run(python_port).api_agreement_pct == 50.0

    def it_reports_a_count_per_outcome(python_port, api_process):
        assert Codebase.from_run(python_port).api_outcomes == {
            "match": 1,
            "mismatch": 1,
            "error_match": 1,
            "error_mismatch": 0,
            "crash": 1,
        }

    def it_reports_the_confusion_counts_by_reference_and_port_status(python_port, api_process):
        confusion = Codebase.from_run(python_port).api_confusion
        assert confusion["ok"] == {"ok": 2, "error": 0, "crash": 1}
        assert confusion["error"]["error"] == 1

    def it_runs_a_python_port_against_the_held_out_corpus_with_the_python_driver(
        python_port, api_process, api_corpus
    ):
        Codebase.from_run(python_port).api_agreement_pct
        argv = measure_api_argv(api_process, "run")
        assert argv[:6] == [
            "measure-api",
            "run",
            "--corpus",
            str(api_corpus),
            "--implementation",
            str(Path(python_port["run_dir"]) / "ported_implementation"),
        ]
        assert argv[argv.index("--language") + 1] == "python"

    def it_runs_a_javascript_port_that_ships_src_index_ts_with_the_typescript_driver(
        javascript_port, api_process
    ):
        Codebase.from_run(javascript_port).api_agreement_pct
        argv = measure_api_argv(api_process, "run")
        assert argv[argv.index("--language") + 1] == "typescript"

    def it_compares_the_port_with_the_reference_cases_of_its_driver(
        javascript_port, api_process, api_corpus
    ):
        Codebase.from_run(javascript_port).api_agreement_pct
        argv = measure_api_argv(api_process, "compare")
        assert argv[argv.index("--reference") + 1] == str(api_corpus / "reference-typescript.jsonl")

    def it_runs_measure_api_from_its_own_package(python_port, api_process):
        Codebase.from_run(python_port).api_agreement_pct
        argv = api_process.run.call_args.args[0]
        assert argv[:4] == ["uv", "run", "--directory", str(codebase_module.MEASURE_API_DIR)]

    def it_gives_a_javascript_port_without_src_index_ts_zero_agreement_and_a_note(
        tmp_path, api_process
    ):
        run = v2_run(tmp_path, "20261012T000000Z_js000003", "javascript")
        (Path(run["run_dir"]) / "ported_implementation" / "index.js").write_text("")
        codebase = Codebase.from_run(run)
        assert codebase.api_agreement_pct == 0.0
        assert codebase.api_outcomes["crash"] == 4
        assert codebase.api_note == "every case crashed: no src/index.ts"
        assert [call.args[0][5] for call in api_process.run.call_args_list] == ["compare"]

    def it_notes_the_first_crash_when_every_case_crashed(python_port, api_process):
        api_process.run.side_effect = respond_to_measure_api(
            [(None, "ModuleNotFoundError: No module named 'gbnf'")] * 4
        )
        codebase = Codebase.from_run(python_port)
        assert codebase.api_agreement_pct == 0.0
        assert codebase.api_note == "every case crashed: ModuleNotFoundError: No module named 'gbnf'"

    def it_has_no_note_when_a_case_ran(python_port, api_process):
        assert Codebase.from_run(python_port).api_note is None

    def it_runs_measure_api_once_for_every_column(python_port, api_process):
        codebase = Codebase.from_run(python_port)
        codebase.api_agreement_pct
        codebase.api_outcomes
        codebase.api_confusion
        codebase.api_note
        assert api_process.run.call_count == 2

    def it_raises_when_measure_api_fails(python_port, api_process):
        api_process.run.side_effect = None
        api_process.run.return_value = Mock(returncode=1, stdout="", stderr="boom")
        with pytest.raises(RuntimeError, match="boom"):
            Codebase.from_run(python_port).api_agreement_pct

    def it_caches_under_codebases_api_by_the_ports_contents():
        assert str(codebase_module.api_cache.path("abc")).endswith("codebases/api/abc.pkl")

    def it_serves_a_port_with_the_same_contents_from_the_cache(
        tmp_path, python_port, api_corpus, api_cached
    ):
        twin = v2_run(tmp_path, "20261012T000000Z_py000003", "python")
        shutil.copytree(
            Path(python_port["run_dir"]) / "ported_implementation",
            Path(twin["run_dir"]) / "ported_implementation",
            dirs_exist_ok=True,
        )
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.side_effect = respond_to_measure_api(PORT_CASES)
            first = Codebase.from_run(python_port).api_agreement_pct
            second = Codebase.from_run(twin).api_agreement_pct
        assert (first, second) == (50.0, 50.0)
        assert m.run.call_count == 2


AST_COMPARE_REPORT = {
    "language": "python",
    "port": "/run/ported_implementation",
    "reference": "/reference/packages/gbnf/python",
    "delta": {"node_count": {"delta": -20, "port": 80, "reference": 100}},
    "functions": {"matched_count": 3, "matched_fraction": 0.75},
    "tree_edit_distance": {"mean_normalised": 0.3, "median_normalised": 0.25},
    "branching": {"port": [1, 2], "reference": [1, 3], "wasserstein": 0.5},
    "api_surface": {"shared": ["GBNF/1"], "port_only": [], "reference_only": ["RuleChar"]},
}


@pytest.fixture
def pinned_reference(monkeypatch, tmp_path):
    checkout = tmp_path / "pinned"
    for language in ("python", "javascript"):
        (checkout / "packages" / "gbnf" / language).mkdir(parents=True)
    monkeypatch.setattr(codebase_module, "REFERENCE_CHECKOUT", checkout)
    return checkout


@pytest.fixture
def ast_compare_process(uncached, pinned_reference):
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.return_value = Mock(returncode=0, stdout=json.dumps(AST_COMPARE_REPORT), stderr="")
        yield m


def measure_ast_compare_argv(process) -> list[str]:
    argv = process.run.call_args.args[0]
    return argv[argv.index("measure-ast") :]


def describe_ast_compare():
    def it_reports_the_compare_json(python_port, ast_compare_process):
        assert Codebase.from_run(python_port).ast_report == AST_COMPARE_REPORT

    def it_has_no_note_when_compare_ran(python_port, ast_compare_process):
        assert Codebase.from_run(python_port).ast_note is None

    def it_runs_measure_ast_compare_from_its_own_package(python_port, ast_compare_process):
        Codebase.from_run(python_port).ast_report
        argv = ast_compare_process.run.call_args.args[0]
        assert argv[:4] == ["uv", "run", "--directory", str(codebase_module.MEASURE_AST_DIR)]

    def it_compares_a_python_port_with_the_pinned_python_reference(
        python_port, ast_compare_process, pinned_reference
    ):
        Codebase.from_run(python_port, ["__pycache__"]).ast_report
        assert measure_ast_compare_argv(ast_compare_process) == [
            "measure-ast",
            "compare",
            "--language",
            "python",
            "--port",
            str(Path(python_port["run_dir"]) / "ported_implementation"),
            "--reference",
            str(pinned_reference / "packages" / "gbnf" / "python"),
            "--exclude",
            "__pycache__",
        ]

    def it_compares_a_javascript_port_as_typescript_with_the_pinned_javascript_reference(
        javascript_port, ast_compare_process, pinned_reference
    ):
        Codebase.from_run(javascript_port, ["node_modules"]).ast_report
        argv = measure_ast_compare_argv(ast_compare_process)
        assert argv[argv.index("--language") + 1] == "typescript"
        assert argv[argv.index("--reference") + 1] == str(
            pinned_reference / "packages" / "gbnf" / "javascript"
        )

    def it_leaves_out_the_javascript_references_build_tooling_on_both_sides(
        javascript_port, ast_compare_process
    ):
        Codebase.from_run(javascript_port, ["node_modules"]).ast_report
        argv = measure_ast_compare_argv(ast_compare_process)
        excluded = [argv[i + 1] for i, arg in enumerate(argv) if arg == "--exclude"]
        assert excluded == ["node_modules", "builder", "dev"]

    def it_notes_the_error_and_reports_nothing_when_compare_exits_non_zero(
        python_port, ast_compare_process
    ):
        ast_compare_process.run.return_value = Mock(
            returncode=1, stdout="", stderr="no python file parsed under /port\n"
        )
        codebase = Codebase.from_run(python_port)
        assert codebase.ast_report is None
        assert codebase.ast_note == "no python file parsed under /port"

    def it_runs_measure_ast_compare_once_for_the_report_and_the_note(
        python_port, ast_compare_process
    ):
        codebase = Codebase.from_run(python_port)
        codebase.ast_report
        codebase.ast_note
        assert ast_compare_process.run.call_count == 1

    def it_caches_under_codebases_ast_by_measure_asts_source_and_the_ports_contents():
        version = codebase_module.content_hash(codebase_module.MEASURE_AST_DIR / "src")
        assert str(codebase_module.ast_cache.path("abc")).endswith(f"codebases/ast/{version}/abc.pkl")

    def it_serves_a_port_with_the_same_contents_from_the_cache(
        monkeypatch, tmp_path, python_port, pinned_reference
    ):
        monkeypatch.setattr(
            codebase_module.ast_cache,
            "path",
            lambda contents, **kwargs: tmp_path / "ast" / f"{contents}.pkl",
        )
        twin = v2_run(tmp_path, "20261012T000000Z_py000004", "python")
        shutil.copytree(
            Path(python_port["run_dir"]) / "ported_implementation",
            Path(twin["run_dir"]) / "ported_implementation",
            dirs_exist_ok=True,
        )
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(
                returncode=0, stdout=json.dumps(AST_COMPARE_REPORT), stderr=""
            )
            first = Codebase.from_run(python_port).ast_report
            second = Codebase.from_run(twin).ast_report
        assert first == second == AST_COMPARE_REPORT
        assert m.run.call_count == 1


def describe_pinned_reference():
    def it_keeps_one_checkout_per_gbnf_commit_beside_the_other_caches():
        assert codebase_module.REFERENCE_CHECKOUT == (
            Path.home()
            / ".cache"
            / "ports"
            / "analysis"
            / "codebases"
            / "reference"
            / codebase_module.GBNF_COMMIT
        )

    def it_pins_the_commit_the_experiment_derives_from():
        config = (
            codebase_module.ANALYSIS.parent
            / "packages"
            / "gbnf_experiment"
            / "src"
            / "gbnf_experiment"
            / "config.py"
        )
        assert f'gbnf_commit: str = "{codebase_module.GBNF_COMMIT}"' in config.read_text()

    def it_fetches_the_pin_and_applies_every_gbnf_prepare_patch(monkeypatch, tmp_path):
        monkeypatch.setattr(codebase_module, "REFERENCE_CHECKOUT", tmp_path / "pinned")
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=0, stdout="", stderr="")
            assert codebase_module.pinned_reference() == tmp_path / "pinned"
        commands = [call.args[0] for call in m.run.call_args_list]
        assert [command[:2] for command in commands] == [["git", "-C"]] * 4
        assert [command[3] for command in commands] == ["init", "fetch", "checkout", "apply"]
        assert commands[1][-2:] == ["https://github.com/thekevinscott/gbnf", codebase_module.GBNF_COMMIT]
        patches = sorted(str(p) for p in codebase_module.PATCHES.glob("*.patch"))
        assert patches
        assert commands[-1][-len(patches) :] == patches
        assert (tmp_path / "pinned").is_dir()

    def it_reuses_an_existing_checkout(monkeypatch, tmp_path):
        (tmp_path / "pinned").mkdir()
        monkeypatch.setattr(codebase_module, "REFERENCE_CHECKOUT", tmp_path / "pinned")
        with patch("src.Codebase.subprocess", autospec=True) as m:
            codebase_module.pinned_reference()
        assert m.run.call_count == 0

    def it_raises_and_leaves_no_checkout_when_git_fails(monkeypatch, tmp_path):
        monkeypatch.setattr(codebase_module, "REFERENCE_CHECKOUT", tmp_path / "pinned")
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=128, stdout="", stderr="fatal: unreachable")
            with pytest.raises(RuntimeError, match="unreachable"):
                codebase_module.pinned_reference()
        assert not (tmp_path / "pinned").exists()
TRANSCRIPT_REPORT = {"turns": 43, "read_source_tests": 3, "suite_run_count": 5}


def write_transcript(run: dict, text: str = '{"type": "assistant"}\n') -> None:
    run_dir = Path(run["run_dir"])
    (run_dir / "manifest.json").write_text(
        json.dumps({"condition": {"source_language": run["source_language"]}})
    )
    projects = run_dir / "transcript" / ".claude" / "projects" / "-target"
    projects.mkdir(parents=True, exist_ok=True)
    (projects / "session.jsonl").write_text(text)


@pytest.fixture
def transcript_run(python_port):
    write_transcript(python_port)
    return python_port


@pytest.fixture
def transcript_process(uncached):
    with patch("src.Codebase.subprocess", autospec=True) as m:
        m.run.return_value = Mock(returncode=0, stdout=json.dumps(TRANSCRIPT_REPORT), stderr="")
        yield m


@pytest.fixture
def transcript_cached(monkeypatch, tmp_path):
    monkeypatch.setattr(
        codebase_module.transcript_cache,
        "path",
        lambda contents, **kwargs: tmp_path / "transcript" / f"{contents}.pkl",
    )


def describe_transcript():
    def it_reports_what_measure_transcript_printed(transcript_run, transcript_process):
        assert Codebase.from_run(transcript_run).transcript == TRANSCRIPT_REPORT

    def it_runs_measure_transcript_on_the_run_directory_from_its_own_package(
        transcript_run, transcript_process
    ):
        Codebase.from_run(transcript_run).transcript
        assert transcript_process.run.call_args.args[0] == [
            "uv",
            "run",
            "--directory",
            str(codebase_module.MEASURE_TRANSCRIPT_DIR),
            "measure-transcript",
            "--run",
            transcript_run["run_dir"],
        ]

    def it_runs_measure_transcript_once_per_codebase(transcript_run, transcript_process):
        codebase = Codebase.from_run(transcript_run)
        codebase.transcript
        codebase.transcript
        assert transcript_process.run.call_count == 1

    def it_raises_when_measure_transcript_prints_no_report(transcript_run, transcript_process):
        transcript_process.run.return_value = Mock(returncode=1, stdout="", stderr="Error: no transcript")
        with pytest.raises(RuntimeError, match="no transcript"):
            Codebase.from_run(transcript_run).transcript

    def it_caches_under_codebases_transcript_by_the_transcripts_contents():
        assert str(codebase_module.transcript_cache.path("abc")).endswith(
            "codebases/transcript/abc.pkl"
        )

    def it_serves_a_run_with_the_same_transcript_from_the_cache(
        tmp_path, transcript_run, transcript_cached
    ):
        twin = v2_run(tmp_path, "20261012T000000Z_py000004", "python")
        write_transcript(twin)
        with patch("src.Codebase.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=0, stdout=json.dumps(TRANSCRIPT_REPORT), stderr="")
            first = Codebase.from_run(transcript_run).transcript
            second = Codebase.from_run(twin).transcript
        assert first == second == TRANSCRIPT_REPORT
        assert m.run.call_count == 1


def describe_transcript_hash():
    def it_matches_for_two_runs_with_the_same_transcript_and_source_language(tmp_path):
        a = v2_run(tmp_path, "a", "python")
        b = v2_run(tmp_path, "b", "python")
        write_transcript(a)
        write_transcript(b)
        assert transcript_hash(Path(a["run_dir"])) == transcript_hash(Path(b["run_dir"]))

    def it_reads_the_transcript_inside_the_hidden_claude_directory(tmp_path):
        run = v2_run(tmp_path, "a", "python")
        write_transcript(run)
        before = transcript_hash(Path(run["run_dir"]))
        write_transcript(run, '{"type": "user"}\n')
        assert transcript_hash(Path(run["run_dir"])) != before

    def it_changes_with_the_source_language_the_paths_are_classed_by(tmp_path):
        a = v2_run(tmp_path, "a", "python")
        b = v2_run(tmp_path, "b", "javascript")
        write_transcript(a)
        write_transcript(b)
        assert transcript_hash(Path(a["run_dir"])) != transcript_hash(Path(b["run_dir"]))

    def it_changes_with_measure_transcripts_source(monkeypatch, tmp_path):
        run = v2_run(tmp_path, "a", "python")
        write_transcript(run)
        package = tmp_path / "measure-transcript"
        (package / "src").mkdir(parents=True)
        (package / "src" / "measure.py").write_text("x = 1\n")
        monkeypatch.setattr(codebase_module, "MEASURE_TRANSCRIPT_DIR", package)
        before = transcript_hash(Path(run["run_dir"]))
        (package / "src" / "measure.py").write_text("x = 2\n")
        assert transcript_hash(Path(run["run_dir"])) != before

    def it_ignores_the_port(tmp_path):
        run = v2_run(tmp_path, "a", "python")
        write_transcript(run)
        before = transcript_hash(Path(run["run_dir"]))
        (Path(run["run_dir"]) / "ported_implementation" / "x.py").write_text("x = 1\n")
        assert transcript_hash(Path(run["run_dir"])) == before
