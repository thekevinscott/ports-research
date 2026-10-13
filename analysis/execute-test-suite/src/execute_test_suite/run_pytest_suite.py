import dataclasses
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from execute_test_suite.adapt_python import REPORT_VARIABLE, TARGET_VARIABLE
from execute_test_suite.parse_coverage_json import parse_coverage_json
from execute_test_suite.parse_junit_report import parse_junit_report
from execute_test_suite.read_adapt_report import read_adapt_report
from execute_test_suite.suite_result import SuiteResult

PYTEST_VERSION = "9.1.1"
PYTEST_DESCRIBE_VERSION = "3.2.0"
PYTEST_COV_VERSION = "7.0.0"
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
    target: Path,
    test_files: list[Path],
    adapt: bool = False,
    coverage: bool = False,
) -> SuiteResult:
    """Run test_files under pinned pytest and pytest-describe, with target as the port root.

    `PYTHONPATH=target` makes `import gbnf` find the port; pytest's own rootdir
    insertion resolves the colocated tests' relative imports. The process runs from
    a scratch directory that holds its reports.

    With `adapt`, the `adapt_python` plugin is copied into the scratch directory
    and loaded with `-p`, so it patches the port's `gbnf` surface before
    collection; the rules it applied come back on the result.

    With `coverage`, pytest-cov measures `target` itself — every file under it,
    imported or not — through a config written into the scratch directory that
    turns on branch mode and omits every test file. Neither the flag nor the
    dependency is passed otherwise, so a run without it is what it always was.
    """
    with tempfile.TemporaryDirectory() as scratch:
        report_path = Path(scratch) / "report.xml"
        adapt_report_path = Path(scratch) / "adapt.json"
        env = {**os.environ, "PYTHONPATH": str(target)}
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
                "--continue-on-collection-errors",
                *plugin,
                *(str(path) for path in test_files),
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
