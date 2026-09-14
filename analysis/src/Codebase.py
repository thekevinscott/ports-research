import json
import math
import statistics
import subprocess
from datetime import timedelta
from fnmatch import fnmatch
from hashlib import sha256
from functools import cached_property, lru_cache
from itertools import chain
from pathlib import Path

import polars as pl
from cachetta import Cachetta
from dirsql._dirsql import DirSQL
from pygount import SourceAnalysis

FILES_SQL = "SELECT path, ext, size FROM './' ORDER BY path"
FILES_SCHEMA = {"path": pl.String, "ext": pl.String, "size": pl.Int64}
EXECUTE_TEST_SUITE_DIR = Path(__file__).resolve().parents[2] / "packages" / "execute-test-suite"
MEASURE_AST_DIR = Path(__file__).resolve().parents[2] / "proposed-projects" / "measure-ast"
MEASURE_EMBEDDING_DIR = Path(__file__).resolve().parents[2] / "proposed-projects" / "measure-embedding"
ROUND_TRIP_DIR = Path(__file__).resolve().parents[2] / "proposed-projects" / "round-trip-experiment"
EXERCISE_API_DIR = Path(__file__).resolve().parents[2] / "proposed-projects" / "exercise-api"
CASES = {
    "generated": EXERCISE_API_DIR / "cases" / "generated-seed0-500.jsonl",
    "fixtures": EXERCISE_API_DIR / "cases" / "fixtures.jsonl",
    "ladder": EXERCISE_API_DIR / "cases" / "ladder.jsonl",
}
LADDER_SLOPE_RUNG = "8-json-depth"
EMBEDDINGS = Path.home() / ".cache" / "ports" / "analysis" / "embeddings-stripped"
EMBEDDING_MODEL = "qwen3-embedding-0.6b-q8_0"

# Ports never change once written, so their test results never expire.
# timedelta.max overflows cachetta's expiry check on read.
disk_cache = Cachetta(path=Path.home() / ".cache" / "ports" / "analysis", duration=timedelta(days=36500))
test_runs_cache = disk_cache / (
    lambda suite, run_id, adapt=False, coverage=False, **kwargs: (
        f"codebases/test-runs/{suite}"
        f"{'-adapt' if adapt else ''}{'-coverage' if coverage else ''}/{run_id}.pkl"
    )
)
exercise_api_cache = disk_cache / (
    lambda case_set, run_id, **kwargs: f"codebases/exercise-api/{case_set}/{run_id}.pkl"
)
reference_diff_cache = disk_cache / (
    lambda reference, target, **kwargs: (
        f"codebases/reference-diff/{sha256(f'{reference}\n{target}'.encode()).hexdigest()}.pkl"
    )
)


def exclude_args(exclude: list[str]) -> list[str]:
    return list(chain.from_iterable(("--exclude", pattern) for pattern in exclude))


def run_tool(directory: Path, *argv: str) -> dict:
    process = subprocess.run(
        ["uv", "run", "--directory", str(directory), *argv], capture_output=True, text=True
    )
    try:
        return json.loads(process.stdout)
    except ValueError:
        raise RuntimeError(
            f"{' '.join(argv)} produced no report (exit {process.returncode}): {process.stderr}"
        )


def _add_ms(entry: dict) -> float:
    return entry["add_ns"]["median"] / 1e6


@lru_cache
def _ladder_index() -> dict[tuple[str, int], int]:
    """Position in the case file, so a rung a port failed is a gap rather than a shift."""
    cases = [json.loads(line) for line in CASES["ladder"].read_text().splitlines()]
    return {(case["rung"], len(case["input"])): index for index, case in enumerate(cases)}


def _log_log_slope(points: list[tuple[float, float]]) -> float | None:
    """Least-squares slope of log(y) against log(x), the measure-complexity-curve formula."""
    if len(points) < 2:
        return None
    xs = [math.log(x) for x, _ in points]
    ys = [math.log(y) for _, y in points]
    mean_x, mean_y = sum(xs) / len(xs), sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator == 0:
        return None
    return sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator


@exercise_api_cache
def run_exercise_api(
    case_set: str, run_id: str, *, language: str, reference: Path, target: Path
) -> dict:
    # The ladder file carries a repeat and warm-up budget per case, so no flag is needed.
    report = run_tool(
        EXERCISE_API_DIR,
        "exercise-api",
        "--language",
        language,
        "--reference",
        str(reference),
        "--target",
        str(target),
        "--cases",
        str(CASES[case_set]),
        "--adapt",
    )
    return report["targets"][str(target)]


@reference_diff_cache
def run_git_diff(reference: Path, target: Path, *, language: str, exclude: list[str]) -> dict:
    return run_tool(
        ROUND_TRIP_DIR,
        "measure-code-distance",
        "git-diff",
        "--language",
        language,
        "--a",
        str(reference),
        "--b",
        str(target),
        *exclude,
    )


@test_runs_cache
def run_test_suite(
    suite: str,
    run_id: str,
    *,
    language: str,
    target: Path,
    adapt: bool = False,
    coverage: bool = False,
) -> dict:
    process = subprocess.run(
        [
            "uv",
            "run",
            "--directory",
            str(EXECUTE_TEST_SUITE_DIR),
            "execute-test-suite",
            "--language",
            language,
            "--target",
            str(target),
            "--suite",
            suite,
            *(["--adapt"] if adapt else []),
            *(["--coverage"] if coverage else []),
        ],
        capture_output=True,
        text=True,
    )
    try:
        return json.loads(process.stdout)
    except ValueError:
        raise RuntimeError(
            f"execute-test-suite {suite} {run_id} produced no report "
            f"(exit {process.returncode}): {process.stderr}"
        )


class Codebase:
    def __init__(
        self,
        path: Path | str,
        exclude: list[str] = [],
        *,
        language: str | None = None,
        reference: Path | str | None = None,
        run_id: str | None = None,
    ):
        self.path = Path(path)
        self.exclude = exclude
        self.language = language
        # The reference has no run row, but it still needs a cache key of its own.
        self.run_id = run_id
        self.reference = None if reference is None else Path(reference)
        self.run: dict | None = None
        rows = DirSQL(str(self.path)).query(FILES_SQL)
        self.files = pl.DataFrame(
            [row for row in rows if not self._excluded(row["path"])], schema=FILES_SCHEMA
        )

    @classmethod
    def from_run(
        cls, run: dict, exclude: list[str] = [], *, reference: Path | str | None = None
    ) -> "Codebase":
        codebase = cls(
            Path(run["run_dir"]) / "ported_implementation",
            exclude,
            language=run["target_language"],
            reference=reference,
            run_id=run["run_id"],
        )
        codebase.run = run
        return codebase

    def _excluded(self, path: str) -> bool:
        candidates = [path, *Path(path).parts]
        return any(fnmatch(c, pattern) for pattern in self.exclude for c in candidates)

    def _analyses(self) -> list[SourceAnalysis]:
        return [
            SourceAnalysis.from_file(str(self.path / p), "codebase", fallback_encoding="utf-8")
            for p in self.files["path"]
        ]

    @property
    def file_count(self) -> int:
        return self.files.height

    @property
    def loc(self) -> int:
        return sum(a.code_count for a in self._analyses())

    @property
    def lines(self) -> int:
        return sum(a.line_count for a in self._analyses())

    @property
    def chars(self) -> int:
        return sum(
            len((self.path / p).read_text(encoding="utf-8", errors="replace"))
            for p in self.files["path"]
        )

    def _report(self, suite: str, adapt: bool = False, coverage: bool = False) -> dict | None:
        if self.run_id is None or self.language is None:
            return None
        return run_test_suite(
            suite,
            self.run_id,
            language=self.language,
            target=self.path,
            adapt=adapt,
            coverage=coverage,
        )

    def _pass_pct(self, suite: str, adapt: bool = False) -> float | None:
        report = self._report(suite, adapt)
        return None if report is None else 100 * report["passed"] / report["total"]

    def _coverage_pct(self, suite: str) -> float | None:
        """Lines of this codebase's own source the adapted suite ran, as a percentage."""
        report = self._report(suite, adapt=True, coverage=True)
        return None if report is None else report["coverage"]["line_pct"]

    @property
    def unit_pass_pct(self) -> float | None:
        return self._pass_pct("unit")

    @property
    def integration_pass_pct(self) -> float | None:
        return self._pass_pct("integration")

    @property
    def adapted_unit_pass_pct(self) -> float | None:
        return self._pass_pct("unit", adapt=True)

    @property
    def adapted_integration_pass_pct(self) -> float | None:
        return self._pass_pct("integration", adapt=True)

    @property
    def adapted_unit_coverage_pct(self) -> float | None:
        return self._coverage_pct("unit")

    @property
    def adapted_integration_coverage_pct(self) -> float | None:
        return self._coverage_pct("integration")

    @property
    def adapt_rules(self) -> str | None:
        report = self._report("unit", adapt=True)
        return None if report is None else ",".join(report["adapt"]["rules_fired"])

    @cached_property
    def _ast(self) -> dict:
        process = subprocess.run(
            [
                "uv",
                "run",
                "--directory",
                str(MEASURE_AST_DIR),
                "measure-ast",
                "--language",
                self.language,
                "--target",
                str(self.path),
                *chain.from_iterable(("--exclude", pattern) for pattern in self.exclude),
            ],
            capture_output=True,
            text=True,
        )
        try:
            return json.loads(process.stdout)
        except ValueError:
            raise RuntimeError(
                f"measure-ast {self.path} produced no report "
                f"(exit {process.returncode}): {process.stderr}"
            )

    def _ast_metric(self, name: str) -> int | float | None:
        return None if self.language is None else self._ast[name]

    @property
    def node_count(self) -> int | None:
        return self._ast_metric("node_count")

    @property
    def max_depth(self) -> int | None:
        return self._ast_metric("max_depth")

    @property
    def function_count(self) -> int | None:
        return self._ast_metric("function_count")

    @property
    def mean_function_lines(self) -> float | None:
        return self._ast_metric("mean_function_lines")

    @property
    def max_function_lines(self) -> int | None:
        return self._ast_metric("max_function_lines")

    @property
    def mean_cyclomatic(self) -> float | None:
        return self._ast_metric("mean_cyclomatic")

    @property
    def max_cyclomatic(self) -> int | None:
        return self._ast_metric("max_cyclomatic")

    def _exclude_args(self) -> list[str]:
        return exclude_args(self.exclude)

    def _embed(self, target: Path, out: Path) -> None:
        run_tool(
            MEASURE_EMBEDDING_DIR,
            "measure-embedding",
            "embed",
            "--language",
            self.language,
            "--target",
            str(target),
            "--out",
            str(out),
            "--model",
            EMBEDDING_MODEL,
            "--strip-comments",
            *self._exclude_args(),
        )

    @cached_property
    def _embedding(self) -> dict:
        out = EMBEDDINGS / "runs" / self.run["run_id"]
        reference_out = EMBEDDINGS / "reference" / self.language
        self._embed(self.path, out)
        self._embed(self.reference, reference_out)
        return run_tool(
            MEASURE_EMBEDDING_DIR,
            "measure-embedding",
            "compare",
            "--a",
            str(out),
            "--b",
            str(reference_out),
        )

    def _embedding_metric(self, name: str) -> float | None:
        return None if self.run is None or self.reference is None else self._embedding[name]

    @property
    def embedding_distance(self) -> float | None:
        return self._embedding_metric("mean_cosine_distance")

    @property
    def embedding_nearest_file_distance(self) -> float | None:
        return self._embedding_metric("mean_nearest_file_distance")

    @property
    def chamfer_distance(self) -> float | None:
        return self._embedding_metric("chamfer_distance")

    @property
    def chamfer_a_to_b(self) -> float | None:
        return self._embedding_metric("chamfer_a_to_b")

    @property
    def chamfer_b_to_a(self) -> float | None:
        return self._embedding_metric("chamfer_b_to_a")

    @cached_property
    def _code_distance(self) -> dict:
        return run_tool(
            ROUND_TRIP_DIR,
            "measure-code-distance",
            "levenshtein",
            "--language",
            self.language,
            "--a",
            str(self.reference),
            "--b",
            str(self.path),
            *self._exclude_args(),
        )

    def _code_distance_metric(self, name: str) -> float | None:
        return None if self.reference is None else self._code_distance[name]

    @property
    def token_levenshtein(self) -> float | None:
        return self._code_distance_metric("token_levenshtein")

    @property
    def char_levenshtein(self) -> float | None:
        return self._code_distance_metric("char_levenshtein")

    @property
    def path_levenshtein(self) -> float | None:
        return self._code_distance_metric("path_levenshtein")

    @cached_property
    def _reference_diff(self) -> dict:
        return run_git_diff(
            self.reference, self.path, language=self.language, exclude=self._exclude_args()
        )

    def _reference_diff_metric(self, name: str) -> int | float | None:
        return None if self.reference is None else self._reference_diff[name]

    @property
    def reference_diff_ratio(self) -> float | None:
        return self._reference_diff_metric("diff_ratio")

    @property
    def reference_diff_identical(self) -> int | None:
        return self._reference_diff_metric("identical")

    @property
    def reference_diff_modified(self) -> int | None:
        return self._reference_diff_metric("modified")

    @property
    def reference_diff_renamed(self) -> int | None:
        return self._reference_diff_metric("renamed")

    @property
    def reference_diff_added(self) -> int | None:
        return self._reference_diff_metric("added")

    @property
    def reference_diff_deleted(self) -> int | None:
        return self._reference_diff_metric("deleted")

    @property
    def reference_diff_similarity_pct(self) -> float | None:
        return self._reference_diff_metric("similarity_pct")

    @property
    def reference_diff_kept_pct(self) -> float | None:
        lines = self._reference_diff_metric("reference_lines")
        if not lines:
            return None
        return 100 * (lines - self._reference_diff["deletions"]) / lines

    def _api(self, case_set: str) -> dict | None:
        if self.run is None or self.reference is None:
            return None
        return run_exercise_api(
            case_set,
            self.run["run_id"],
            language=self.language,
            reference=self.reference,
            target=self.path,
        )

    def _api_agreement_pct(self, case_set: str) -> float | None:
        result = self._api(case_set)
        return None if result is None else 100 * result["agree_with_reference"] / result["cases"]

    @property
    def api_agreement_pct(self) -> float | None:
        return self._api_agreement_pct("generated")

    @property
    def api_fixture_agreement_pct(self) -> float | None:
        return self._api_agreement_pct("fixtures")

    @property
    def api_p50_ms(self) -> float | None:
        result = self._api("generated")
        return None if result is None else result["target_p50_elapsed_ns"] / 1e6

    def _ladder(self, key: str) -> list[dict] | None:
        # A driver that failed every case carries no timings at all, so the key is absent.
        result = self._api("ladder")
        return None if result is None else result.get(key)

    def _ladder_median_ms(self, key: str) -> float | None:
        timings = self._ladder(key)
        return None if not timings else statistics.median(_add_ms(entry) for entry in timings)

    @property
    def ladder_timings(self) -> list[dict] | None:
        return self._ladder("timings")

    @property
    def ladder_reference_timings(self) -> list[dict] | None:
        return self._ladder("reference_timings")

    @property
    def ladder_median_ms(self) -> float | None:
        return self._ladder_median_ms("timings")

    def _ladder_slope(self, key: str) -> float | None:
        timings = self._ladder(key)
        if timings is None:
            return None
        return _log_log_slope(
            [
                (entry["input_len"], _add_ms(entry))
                for entry in timings
                if entry["rung"] == LADDER_SLOPE_RUNG
            ]
        )

    @property
    def ladder_slope(self) -> float | None:
        return self._ladder_slope("timings")

    @property
    def ladder_reference_slope(self) -> float | None:
        return self._ladder_slope("reference_timings")

    @property
    def ladder_ref_ratio(self) -> float | None:
        target = self._ladder_median_ms("timings")
        reference = self._ladder_median_ms("reference_timings")
        return None if target is None or not reference else target / reference

    def _ladder_rungs(self, key: str) -> list[dict] | None:
        timings = self._ladder(key)
        if timings is None:
            return None
        index = _ladder_index()
        return [
            {
                "index": index.get((entry["rung"], entry["input_len"])),
                "rung": entry["rung"],
                "input_len": entry["input_len"],
                "ms": _add_ms(entry),
            }
            for entry in timings
        ]

    @property
    def ladder_rungs(self) -> list[dict] | None:
        return self._ladder_rungs("timings")

    @property
    def ladder_reference_rungs(self) -> list[dict] | None:
        return self._ladder_rungs("reference_timings")

    @property
    def ladder_rungs_completed(self) -> int | None:
        timings = self._ladder("timings")
        return None if timings is None else len(timings)

    def _ladder_total_ms(self, key: str) -> float | None:
        timings = self._ladder(key)
        return None if not timings else sum(_add_ms(entry) for entry in timings)

    @property
    def ladder_total_ms(self) -> float | None:
        return self._ladder_total_ms("timings")

    @property
    def ladder_reference_total_ms(self) -> float | None:
        return self._ladder_total_ms("reference_timings")
