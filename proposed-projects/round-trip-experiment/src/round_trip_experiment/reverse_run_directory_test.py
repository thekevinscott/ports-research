from pathlib import Path

import pytest

from round_trip_experiment.reverse_run_directory import reverse_run_directory


@pytest.fixture
def root(tmp_path: Path) -> Path:
    directory = tmp_path / "reverse" / "20260909T001426Z_1c28aa33"
    directory.mkdir(parents=True)
    return directory


def describe_reverse_run_directory():
    def it_finds_the_directory_the_leg_added(root):
        (root / "20260909T021103Z_9f0a1b2c").mkdir()
        assert reverse_run_directory(root, before=set()) == root / "20260909T021103Z_9f0a1b2c"

    def it_ignores_directories_that_were_already_there(root):
        (root / "20260909T021103Z_9f0a1b2c").mkdir()
        (root / "20260909T034500Z_0d0e0f10").mkdir()
        assert reverse_run_directory(root, before={"20260909T021103Z_9f0a1b2c"}) == (
            root / "20260909T034500Z_0d0e0f10"
        )

    def it_takes_the_latest_when_a_leg_left_more_than_one(root):
        (root / "20260909T021103Z_9f0a1b2c").mkdir()
        (root / "20260909T034500Z_0d0e0f10").mkdir()
        assert reverse_run_directory(root, before=set()) == root / "20260909T034500Z_0d0e0f10"

    def it_finds_nothing_when_the_leg_added_nothing(root):
        (root / "20260909T021103Z_9f0a1b2c").mkdir()
        assert reverse_run_directory(root, before={"20260909T021103Z_9f0a1b2c"}) is None

    def it_finds_nothing_when_the_root_was_never_created(tmp_path):
        assert reverse_run_directory(tmp_path / "nowhere", before=set()) is None

    def it_ignores_files(root):
        (root / "notes.md").write_text("not a run")
        assert reverse_run_directory(root, before=set()) is None
