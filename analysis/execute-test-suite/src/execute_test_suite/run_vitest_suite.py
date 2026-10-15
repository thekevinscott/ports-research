import dataclasses
import json
import subprocess
import tempfile
from pathlib import Path

from execute_test_suite.adapt_typescript import adapt_typescript
from execute_test_suite.parse_coverage_summary import parse_coverage_summary
from execute_test_suite.parse_vitest_report import parse_vitest_report
from execute_test_suite.read_adapt_report import read_adapt_report
from execute_test_suite.suite_result import SuiteResult

VITEST_VERSION = "2.1.3"
PORT_ENTRY_FILE = "src/index.ts"
PORT_SOURCE_GLOB = "src/**"
COVERAGE_PACKAGE = "@vitest/coverage-v8"
COVERAGE_DIRECTORY = "coverage"
COVERAGE_SUMMARY_FILE = "coverage-summary.json"
VITEST_BIN = Path("node_modules") / ".bin" / "vitest"
COVERAGE_EXCLUDE = (
    "**/*.test.ts",
    "**/*.test.js",
    "**/*.spec.ts",
    "**/*.spec.js",
    "**/tests/**",
    "**/test/**",
    "**/node_modules/**",
    "**/dist/**",
)
SCRATCH_PACKAGE_JSON = '{"name": "execute-test-suite-scratch", "private": true}'
# Vite skips its per-file tsconfig lookup only when tsconfigRaw is a string; an object is
# merged into whatever it read from disk. Without the bypass a target whose tsconfig
# extends a path outside its own tree fails to transform, and otherwise each target grades
# under whichever tsconfig happens to sit above it. These are the fields esbuild reads.
TSCONFIG_RAW = '{"compilerOptions": {"target": "esnext", "useDefineForClassFields": true}}'
# pnpm 10+ exits 1 (ERR_PNPM_IGNORED_BUILDS) when a dependency's build script is not
# allow-listed, and esbuild has one (it comes in under vite).
ALLOW_BUILD_FLAG = "--allow-build=esbuild"

CONFIG_TEMPLATE = """export default {{
  test: {{
    include: {include},
    globals: true,
  }},
  esbuild: {{
    tsconfigRaw: {tsconfig_raw},
  }},
  resolve: {{
    alias: {{
      gbnf: {alias},
    }},
  }},
}};
"""


def run_vitest_suite(
    *,
    target: Path,
    test_files: list[Path],
    adapt: bool = False,
    coverage: bool = False,
) -> SuiteResult:
    """Run test_files under pinned vitest with `gbnf` aliased to target's `src/index.ts`.

    The config is written into a scratch directory, which is vite's root and holds
    every report.

    With `adapt`, the alias points at a generated shim over that entry file instead,
    and the rules the shim applied come back on the result.

    Every target is transformed under one pinned `tsconfigRaw` rather than the tsconfig
    vite would find next to its files: the hand-written reference's tsconfig extends the
    monorepo root's, which the prepared tree does not carry, and vite treats that
    unresolvable extends as a transform failure — the entry never loads and the suite
    collects nothing.

    With `coverage`, the v8 provider measures the port's own `src/`. Two details
    are load-bearing: `pnpm dlx` cannot serve the provider, because vite resolves
    it from the run's root, so both packages are installed into the scratch
    directory and vitest is invoked from there; and `allowExternal` is required
    because the port sits outside that root, which the provider otherwise treats
    as nothing to measure and reports as zero.
    """
    with tempfile.TemporaryDirectory() as scratch:
        config_path = Path(scratch) / "vitest.config.mjs"
        report_path = Path(scratch) / "report.json"
        adapt_report_path = Path(scratch) / "adapt.json"
        entry = target / PORT_ENTRY_FILE
        if adapt:
            entry = adapt_typescript(
                Path(scratch) / "shim", port_entry=entry, report_path=adapt_report_path
            )
        config_path.write_text(
            CONFIG_TEMPLATE.format(
                include=json.dumps([str(path) for path in test_files]),
                tsconfig_raw=json.dumps(TSCONFIG_RAW),
                alias=json.dumps(str(entry)),
            )
        )
        coverage_directory = Path(scratch) / COVERAGE_DIRECTORY
        vitest = ["pnpm", "dlx", f"vitest@{VITEST_VERSION}"]
        coverage_flags = []
        if coverage:
            (Path(scratch) / "package.json").write_text(SCRATCH_PACKAGE_JSON)
            install = subprocess.run(
                [
                    "pnpm",
                    "--dir",
                    str(scratch),
                    "add",
                    "--save-dev",
                    ALLOW_BUILD_FLAG,
                    f"vitest@{VITEST_VERSION}",
                    f"{COVERAGE_PACKAGE}@{VITEST_VERSION}",
                ],
                cwd=scratch,
                capture_output=True,
                text=True,
            )
            if install.returncode:
                raise RuntimeError(
                    f"could not install {COVERAGE_PACKAGE} "
                    f"(exit {install.returncode}): {install.stderr}{install.stdout}"
                )
            vitest = [str(Path(scratch) / VITEST_BIN)]
            coverage_flags = [
                "--coverage.enabled",
                "--coverage.provider=v8",
                "--coverage.allowExternal",
                "--coverage.reportOnFailure",
                f"--coverage.include={target / PORT_SOURCE_GLOB}",
                *(f"--coverage.exclude={pattern}" for pattern in COVERAGE_EXCLUDE),
                "--coverage.reporter=json-summary",
                f"--coverage.reportsDirectory={coverage_directory}",
            ]
        process = subprocess.run(
            [
                *vitest,
                "run",
                "--config",
                str(config_path),
                "--reporter=json",
                f"--outputFile={report_path}",
                *coverage_flags,
            ],
            cwd=scratch,
            capture_output=True,
            text=True,
        )
        if not report_path.is_file():
            raise RuntimeError(
                f"vitest produced no report (exit {process.returncode}): {process.stderr}"
            )
        result = parse_vitest_report(report_path)
        if coverage:
            summary_path = coverage_directory / COVERAGE_SUMMARY_FILE
            if not summary_path.is_file():
                raise RuntimeError(
                    f"vitest produced no coverage summary (exit {process.returncode}): "
                    f"{process.stderr}"
                )
            result = dataclasses.replace(result, coverage=parse_coverage_summary(summary_path))
        if adapt:
            result = dataclasses.replace(
                result, rules_fired=read_adapt_report(adapt_report_path)
            )
        return result
