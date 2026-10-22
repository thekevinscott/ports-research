"""What a real port leaves behind, read only off disk.

Everything here is an artifact of one `run_gbnf_experiment` invocation against
a temporary data directory. Nothing calls into the package: a run record that
cannot be checked from the outside is a run record nobody can audit later.
"""

import json
import re
from pathlib import Path

import pytest

RUN_DIRECTORY_NAME = re.compile(r"\d{8}T\d{6}Z_[0-9a-f]{8}")
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def manifest(completed_run: Path) -> dict:
    return json.loads((completed_run / "manifest.json").read_text())


def describe_the_run_directory():
    def it_lands_one_directory_in_the_data_tree(
        completed_run: Path, experiment_data: Path
    ):
        assert list(experiment_data.iterdir()) == [completed_run]

    def it_is_stamped_with_utc_and_a_random_token(completed_run: Path):
        assert RUN_DIRECTORY_NAME.fullmatch(completed_run.name)


def describe_the_manifest():
    def it_names_the_image_that_ran_by_id(manifest: dict):
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", manifest["sandbox"]["image_id"])

    def it_records_a_non_empty_source(manifest: dict):
        """The pilot of 2026-10-11 ran on an empty source: `"included": []`."""
        assert manifest["reference_implementation"]["included"]

    def it_records_the_source_in_upstream_layout(manifest: dict):
        """No flags: the python package alone, under python/."""
        assert all(
            path.startswith("python/")
            for path in manifest["reference_implementation"]["included"]
        )

    def it_records_exactly_the_files_the_prepare_image_extracts(manifest: dict):
        listing = FIXTURES / "python_unit-false_source-integration-false_target-integration-false.txt"
        expected = listing.read_text().splitlines()
        assert manifest["reference_implementation"]["included"] == sorted(expected)

    def it_records_the_exit_code(manifest: dict):
        assert manifest["exit_code"] == 0


def describe_the_banked_evidence():
    def it_banks_the_session_result(completed_run: Path):
        result = json.loads((completed_run / "result.json").read_text())
        assert result["is_error"] is False

    def it_banks_stderr_beside_the_result(completed_run: Path):
        assert (completed_run / "stderr.txt").is_file()

    def it_banks_the_proxy_denial_log(completed_run: Path):
        assert (completed_run / "proxy.log").read_text().strip()

    def it_banks_a_transcript(completed_run: Path):
        assert [path for path in (completed_run / "transcript").rglob("*.jsonl")]

    def it_banks_a_ported_implementation(completed_run: Path):
        port = completed_run / "ported_implementation"
        assert [path for path in port.rglob("*") if path.is_file()]
