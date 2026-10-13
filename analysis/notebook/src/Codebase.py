import json
import os
import subprocess
from datetime import timedelta
from fnmatch import fnmatch
from hashlib import sha256
from functools import cache, cached_property
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory

import polars as pl
from cachetta import Cachetta
from dirsql._dirsql import DirSQL
from pygount import SourceAnalysis

from src.embedding_server_key import embedding_server_key

FILES_SQL = "SELECT path, ext, size FROM './' ORDER BY path"
FILES_SCHEMA = {"path": pl.String, "ext": pl.String, "size": pl.Int64}
ANALYSIS = Path(__file__).resolve().parents[2]
EXECUTE_TEST_SUITE_DIR = ANALYSIS / "execute-test-suite"
MEASURE_AST_DIR = ANALYSIS / "measure-ast"
MEASURE_EMBEDDING_DIR = ANALYSIS / "measure-embedding"
ROUND_TRIP_DIR = ANALYSIS / "round-trip-experiment"
MEASURE_BEHAVIOR_DIR = ANALYSIS / "measure-behavior"
MEASURE_API_DIR = ANALYSIS / "measure-api"
MEASURE_TRANSCRIPT_DIR = ANALYSIS / "measure-transcript"
# The held-out corpora: generated grammars and inputs no agent container ever mounts.
BEHAVIOR_CORPUS = MEASURE_BEHAVIOR_DIR / "corpus"
API_CORPUS = MEASURE_API_DIR / "corpus"
# measure-behavior and measure-api load a javascript port through their typescript driver;
# measure-ast parses it with its typescript grammar.
DRIVERS = {"python": "python", "javascript": "typescript"}
# The gbnf pin: packages/gbnf_experiment/src/gbnf_experiment/config.py `gbnf_commit`.
GBNF_COMMIT = "13f1aca495d11e160fffd68c4ba299a2415909d8"
PATCHES = ANALYSIS.parent / "packages" / "gbnf_experiment" / "docker" / "gbnf-prepare" / "patches"
REFERENCE_CHECKOUT = Path.home() / ".cache" / "ports" / "analysis" / "codebases" / "reference" / GBNF_COMMIT
# The javascript reference's build tooling, left out as measure-ast's reference-measures recipe
# does. compare applies every pattern to both sides.
REFERENCE_EXCLUDE = {"python": [], "javascript": ["builder", "dev"]}
# Installed dependencies and caches are not the port's own code.
CONTENT_SKIP = {"node_modules", "__pycache__"}
EMBEDDING_MODEL = "qwen3-embedding-0.6b-q8_0"
# The cache is keyed on the server's model file and pooling; new vectors come only from a server that matches.
EMBEDDING_SERVER = "qwen3-embedding-0.6b-q8_0-pooling-last"
EMBEDDINGS = Path.home() / ".cache" / "ports" / "analysis" / "embeddings-stripped" / EMBEDDING_SERVER
# Reference vectors are keyed by the gbnf commit they were embedded from.
REFERENCE_EMBEDDINGS = EMBEDDINGS / "reference" / GBNF_COMMIT


@cache
def check_embedding_server() -> None:
    """Raise unless the server at GENERATE_EMBEDDING_BASE_URL runs EMBEDDING_MODEL from the file and pooling the cache is keyed on."""
    url = os.environ.get("GENERATE_EMBEDDING_BASE_URL")
    if not url:
        raise RuntimeError("set GENERATE_EMBEDDING_BASE_URL to the embedding server's /v1 url")
    if (served := embedding_server_key(url, EMBEDDING_MODEL)) != EMBEDDING_SERVER:
        raise RuntimeError(f"{url} serves {served}; the embedding cache holds {EMBEDDING_SERVER}")

# Ports never change once written, so their test results never expire.
# timedelta.max overflows cachetta's expiry check on read.
disk_cache = Cachetta(path=Path.home() / ".cache" / "ports" / "analysis", duration=timedelta(days=36500))
test_runs_cache = disk_cache / (
    lambda suite, run_id, adapt=False, coverage=False, **kwargs: (
        f"codebases/test-runs/{suite}"
        f"{'-adapt' if adapt else ''}{'-coverage' if coverage else ''}/{run_id}.pkl"
    )
)
reference_diff_cache = disk_cache / (
    lambda reference, target, **kwargs: (
        f"codebases/reference-diff/{sha256(f'{reference}\n{target}'.encode()).hexdigest()}.pkl"
    )
)

behavior_cache = disk_cache / (lambda contents, **kwargs: f"codebases/behavior/{contents}.pkl")
api_cache = disk_cache / (lambda contents, **kwargs: f"codebases/api/{contents}.pkl")
# A change to measure-ast's source changes its report, so the source hash keys the cache too.
ast_cache = disk_cache / (
    lambda contents, **kwargs: f"codebases/ast/{MEASURE_AST_VERSION}/{contents}.pkl"
)
transcript_cache = disk_cache / (lambda contents, **kwargs: f"codebases/transcript/{contents}.pkl")


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


def content_hash(path: Path) -> str:
    digest = sha256()
    for directory, dirnames, filenames in os.walk(path):
        dirnames[:] = sorted(
            name for name in dirnames if name not in CONTENT_SKIP and not name.startswith(".")
        )
        for name in sorted(filenames):
            file = Path(directory) / name
            if file.is_symlink():
                continue
            digest.update(f"{file.relative_to(path)}\n".encode())
            digest.update(sha256(file.read_bytes()).digest())
    return digest.hexdigest()


MEASURE_AST_VERSION = content_hash(MEASURE_AST_DIR / "src")


def transcript_hash(run_dir: Path) -> str:
    """The run's transcripts, hidden directories included, the source language that classes their paths, and measure-transcript's source, so a changed measure is rerun."""
    digest = sha256()
    digest.update(f"{content_hash(MEASURE_TRANSCRIPT_DIR / 'src')}\n".encode())
    condition = json.loads((run_dir / "manifest.json").read_text())["condition"]
    digest.update(f"{condition['source_language']}\n".encode())
    for file in sorted((run_dir / "transcript").rglob("*.jsonl")):
        digest.update(f"{file.relative_to(run_dir)}\n".encode())
        digest.update(sha256(file.read_bytes()).digest())
    return digest.hexdigest()


@transcript_cache
def run_measure_transcript(contents: str, *, run_dir: Path) -> dict:
    return run_tool(MEASURE_TRANSCRIPT_DIR, "measure-transcript", "--run", str(run_dir))


def run_cli(directory: Path, *argv: str) -> None:
    process = subprocess.run(
        ["uv", "run", "--directory", str(directory), *argv], capture_output=True, text=True
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"{' '.join(argv)} failed (exit {process.returncode}): {process.stderr}"
        )


def driver_can_load(implementation: Path, driver: str) -> bool:
    """The typescript driver loads src/index.ts; without one there is no module to load."""
    return driver != "typescript" or (implementation / "src" / "index.ts").is_file()


@behavior_cache
def run_measure_behavior(contents: str, *, implementation: Path, language: str) -> dict:
    driver = DRIVERS[language]
    reference = BEHAVIOR_CORPUS / f"reference-{driver}.jsonl"
    with TemporaryDirectory() as scratch:
        outcomes = Path(scratch) / "outcomes.jsonl"
        report = Path(scratch) / "report.json"
        if not driver_can_load(implementation, driver):
            # Every pair crashes, as a load failure does.
            outcomes.write_text(
                "".join(
                    json.dumps({**json.loads(line), "outcome": "crash", "error": "no src/index.ts"})
                    + "\n"
                    for line in reference.read_text().splitlines()
                )
            )
        else:
            run_cli(
                MEASURE_BEHAVIOR_DIR,
                "measure-behavior",
                "run",
                "--corpus",
                str(BEHAVIOR_CORPUS),
                "--implementation",
                str(implementation),
                "--language",
                driver,
                "--out",
                str(outcomes),
            )
        run_cli(
            MEASURE_BEHAVIOR_DIR,
            "measure-behavior",
            "compare",
            "--reference",
            str(reference),
            "--port",
            str(outcomes),
            "--out",
            str(report),
        )
        port = [json.loads(line) for line in outcomes.read_text().splitlines()]
        note = (
            f"every pair crashed: {port[0]['error']}"
            if all(pair["outcome"] == "crash" for pair in port)
            else None
        )
        return {**json.loads(report.read_text()), "note": note}


@api_cache
def run_measure_api(contents: str, *, implementation: Path, language: str) -> dict:
    driver = DRIVERS[language]
    reference = API_CORPUS / f"reference-{driver}.jsonl"
    with TemporaryDirectory() as scratch:
        cases = Path(scratch) / "cases.jsonl"
        report = Path(scratch) / "report.json"
        if not driver_can_load(implementation, driver):
            # Every case crashes, as a load failure does.
            cases.write_text(
                "".join(
                    json.dumps({**json.loads(line), "steps": None, "crash": "no src/index.ts"})
                    + "\n"
                    for line in reference.read_text().splitlines()
                )
            )
        else:
            run_cli(
                MEASURE_API_DIR,
                "measure-api",
                "run",
                "--corpus",
                str(API_CORPUS),
                "--implementation",
                str(implementation),
                "--language",
                driver,
                "--out",
                str(cases),
            )
        run_cli(
            MEASURE_API_DIR,
            "measure-api",
            "compare",
            "--reference",
            str(reference),
            "--port",
            str(cases),
            "--out",
            str(report),
        )
        port = [json.loads(line) for line in cases.read_text().splitlines()]
        note = (
            f"every case crashed: {port[0]['crash']}"
            if all(case["crash"] is not None for case in port)
            else None
        )
        return {**json.loads(report.read_text()), "note": note}


def pinned_reference() -> Path:
    """The gbnf pin with the gbnf-prepare patches applied, checked out once and kept."""
    if REFERENCE_CHECKOUT.is_dir():
        return REFERENCE_CHECKOUT
    REFERENCE_CHECKOUT.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=REFERENCE_CHECKOUT.parent) as scratch:
        checkout = Path(scratch) / "checkout"
        checkout.mkdir()
        for command in (
            ["init", "-q"],
            ["fetch", "-q", "--depth", "1", "https://github.com/thekevinscott/gbnf", GBNF_COMMIT],
            ["checkout", "-q", "FETCH_HEAD"],
            ["apply", *sorted(str(patch) for patch in PATCHES.glob("*.patch"))],
        ):
            process = subprocess.run(
                ["git", "-C", str(checkout), *command], capture_output=True, text=True
            )
            if process.returncode != 0:
                raise RuntimeError(
                    f"git {command[0]} failed (exit {process.returncode}): {process.stderr}"
                )
        checkout.rename(REFERENCE_CHECKOUT)
    return REFERENCE_CHECKOUT


@ast_cache
def run_measure_ast_compare(
    contents: str, *, implementation: Path, language: str, exclude: list[str]
) -> dict:
    reference = pinned_reference() / "packages" / "gbnf" / language
    process = subprocess.run(
        [
            "uv",
            "run",
            "--directory",
            str(MEASURE_AST_DIR),
            "measure-ast",
            "compare",
            "--language",
            DRIVERS[language],
            "--port",
            str(implementation),
            "--reference",
            str(reference),
            *exclude_args([*exclude, *REFERENCE_EXCLUDE[language]]),
        ],
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        return {"report": None, "note": process.stderr.strip()}
    return {"report": json.loads(process.stdout), "note": None}


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
        check_embedding_server()
        out = EMBEDDINGS / "runs" / self.run["run_id"]
        reference_out = REFERENCE_EMBEDDINGS / self.language
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

    @cached_property
    def _contents(self) -> str:
        return content_hash(self.path)

    @cached_property
    def _behavior(self) -> dict:
        return run_measure_behavior(
            self._contents, implementation=self.path, language=self.language
        )

    @property
    def behavior_agreement_pct(self) -> float:
        return 100 * self._behavior["agreements"] / self._behavior["pairs"]

    @property
    def behavior_confusion(self) -> dict[str, dict[str, int]]:
        return self._behavior["confusion"]

    @property
    def behavior_note(self) -> str | None:
        return self._behavior["note"]

    @cached_property
    def _api(self) -> dict:
        return run_measure_api(self._contents, implementation=self.path, language=self.language)

    @property
    def api_agreement_pct(self) -> float:
        return 100 * self._api["agreements"] / self._api["cases"]

    @property
    def api_outcomes(self) -> dict[str, int]:
        return self._api["outcomes"]

    @property
    def api_confusion(self) -> dict[str, dict[str, int]]:
        return self._api["confusion"]

    @property
    def api_note(self) -> str | None:
        return self._api["note"]

    @cached_property
    def _ast_compare(self) -> dict:
        return run_measure_ast_compare(
            self._contents, implementation=self.path, language=self.language, exclude=self.exclude
        )

    @property
    def ast_report(self) -> dict | None:
        """measure-ast compare against the pinned reference; None when it exited non-zero."""
        return self._ast_compare["report"]

    @property
    def ast_note(self) -> str | None:
        return self._ast_compare["note"]

    @cached_property
    def transcript(self) -> dict:
        """measure-transcript's report on the run's transcripts."""
        run_dir = Path(self.run["run_dir"])
        return run_measure_transcript(transcript_hash(run_dir), run_dir=run_dir)
