import dataclasses
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .adapt_python import REPORT_VARIABLE, TARGET_VARIABLE
from .parse_coverage_json import parse_coverage_json
from .parse_junit_report import parse_junit_report
from .read_adapt_report import read_adapt_report
from .suite_result import SuiteResult

PYTEST_VERSION = "9.1.1"
PYTEST_DESCRIBE_VERSION = "3.2.0"
PYTEST_COV_VERSION = "7.0.0"
INTEGRATION_TEST_FILE = "iteration/grammars_test.py"
ADAPT_PLUGIN = "adapt_python"
COVERAGE_CONFIG_FILE = ".coveragerc"
COVERAGE_OMIT = (
    "*/tests/*",
    "*/test/*",
    "*/integration-tests/*",
    "*/conftest.py",
    "*_test.py",
    "test_*.py",
    "*/dev-deps/*",
    "*/.venv/*",
    "*/node_modules/*",
)
COVERAGE_CONFIG_TEMPLATE = """[run]
branch = True
omit =
{omit}
"""


def run_pytest_suite(
    *,
    test_suite_directory: Path,
    target: Path,
    suite: str | None = None,
    adapt: bool = False,
    coverage: bool = False,
) -> SuiteResult:
    """Run test_suite_directory as pytest, with target importable as the port root.

    Pinned to the same interpreter the derivation's own README documents
    (`uv run --with pytest==... --with pytest-describe==...`), so a port that
    passed in-sandbox passes the same way here. `PYTHONPATH=target` stands in for
    that README's `cd <port>; python -m pytest tests` cwd trick without running
    pytest inside the port or the read-only test suite — neither is written to;
    the process runs from a scratch directory instead.

    With `adapt`, the `adapt_python` plugin is copied into the scratch directory
    and loaded with `-p`, so it patches the port's `gbnf` surface before
    collection; the rules it applied come back on the result.

    With `coverage`, pytest-cov measures `target` itself — every file under it,
    imported or not — through a config written into the scratch directory that
    turns on branch mode and omits the port's own tests. Neither the flag nor the
    dependency is passed otherwise, so a run without it is what it always was.
    """
    integration_test = test_suite_directory / INTEGRATION_TEST_FILE
    selection = {
        None: [str(test_suite_directory)],
        "unit": [str(test_suite_directory), f"--ignore={integration_test}"],
        "integration": [str(integration_test)],
    }[suite]
    with tempfile.TemporaryDirectory() as scratch:
        report_path = Path(scratch) / "report.xml"
        adapt_report_path = Path(scratch) / "adapt.json"
        env = {**os.environ, "PYTHONPATH": str(target), "PYTHONDONTWRITEBYTECODE": "1"}
        plugin = []
        if adapt:
            shutil.copy(Path(__file__).with_name(f"{ADAPT_PLUGIN}.py"), scratch)
            plugin = ["-p", ADAPT_PLUGIN]
            env |= {
                "PYTHONPATH": f"{target}{os.pathsep}{scratch}",
                TARGET_VARIABLE: str(target),
                REPORT_VARIABLE: str(adapt_report_path),
            }
        coverage_path = Path(scratch) / "coverage.json"
        coverage_dependency = []
        coverage_flags = []
        if coverage:
            config_path = Path(scratch) / COVERAGE_CONFIG_FILE
            config_path.write_text(
                COVERAGE_CONFIG_TEMPLATE.format(
                    omit="\n".join(f"    {pattern}" for pattern in COVERAGE_OMIT)
                )
            )
            coverage_dependency = ["--with", f"pytest-cov=={PYTEST_COV_VERSION}"]
            coverage_flags = [
                f"--cov={target}",
                f"--cov-config={config_path}",
                f"--cov-report=json:{coverage_path}",
            ]
        process = subprocess.run(
            [
                "uv",
                "run",
                "--no-project",
                "--with",
                f"pytest=={PYTEST_VERSION}",
                "--with",
                f"pytest-describe=={PYTEST_DESCRIBE_VERSION}",
                *coverage_dependency,
                "python",
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                *plugin,
                *selection,
                f"--junit-xml={report_path}",
                *coverage_flags,
                "-q",
            ],
            cwd=scratch,
            env=env,
            capture_output=True,
            text=True,
        )
        if not report_path.is_file():
            raise RuntimeError(
                f"pytest produced no report (exit {process.returncode}): {process.stderr}"
            )
        result = parse_junit_report(report_path)
        if coverage:
            if not coverage_path.is_file():
                raise RuntimeError(
                    f"pytest produced no coverage report (exit {process.returncode}): "
                    f"{process.stderr}"
                )
            result = dataclasses.replace(result, coverage=parse_coverage_json(coverage_path))
        if adapt:
            result = dataclasses.replace(
                result, rules_fired=read_adapt_report(adapt_report_path)
            )
        return result
