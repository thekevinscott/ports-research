from pathlib import Path
from unittest.mock import patch

import pytest

from agent_harness_sandbox.utils.scratch_copy import scratch_copy


class SandboxError(Exception):
    """Stands in for the package's error type, a collaborator like any other."""


@pytest.fixture(autouse=True)
def sandbox_error():
    with patch("agent_harness_sandbox.utils.scratch_copy.AgentHarnessSandboxError", SandboxError):
        yield


@pytest.fixture
def source(tmp_path):
    directory = tmp_path / "data"
    directory.mkdir()
    return directory


def describe_scratch_copy():
    def describe_what_it_yields():
        def it_yields_a_directory_of_its_own(source):
            with scratch_copy(source) as copy:
                assert copy.is_dir()
                assert copy.resolve() != source.resolve()

        def it_holds_the_folders_files(source):
            (source / "a.txt").write_text("x")
            with scratch_copy(source) as copy:
                assert (copy / "a.txt").read_text() == "x"

        def it_holds_the_folders_nested_files(source):
            (source / "nested").mkdir()
            (source / "nested" / "a.txt").write_text("x")
            with scratch_copy(source) as copy:
                assert (copy / "nested" / "a.txt").read_text() == "x"

        def it_copies_symlinks_as_symlinks(source, tmp_path):
            target = tmp_path / "outside.txt"
            target.write_text("x")
            (source / "link.txt").symlink_to(target)
            with scratch_copy(source) as copy:
                assert (copy / "link.txt").is_symlink()

        def it_takes_a_string_path(source):
            with scratch_copy(str(source)) as copy:
                assert isinstance(copy, Path)

    def describe_the_copy():
        def it_keeps_writes_out_of_the_source(source):
            with scratch_copy(source) as copy:
                (copy / "installed.txt").write_text("from the container")
            assert sorted(p.name for p in source.iterdir()) == []

        def it_discards_the_copy_after_the_block(source):
            with scratch_copy(source) as copy:
                pass
            assert not copy.exists()

        def it_discards_the_copy_after_an_exception(source):
            with pytest.raises(RuntimeError), scratch_copy(source) as copy:
                held = copy
                raise RuntimeError("boom")
            assert not held.exists()

    def describe_a_refused_folder():
        def it_refuses_a_folder_that_is_not_there(tmp_path):
            with pytest.raises(SandboxError, match="does not exist"):
                with scratch_copy(tmp_path / "gone"):
                    pass

        def it_refuses_a_path_that_is_not_a_folder(tmp_path):
            data = tmp_path / "file"
            data.touch()
            with pytest.raises(SandboxError, match="not a directory"):
                with scratch_copy(data):
                    pass
