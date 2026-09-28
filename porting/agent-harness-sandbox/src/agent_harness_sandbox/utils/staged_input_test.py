from pathlib import Path
from unittest.mock import patch

import pytest

from agent_harness_sandbox.utils.staged_input import staged_input


class SandboxError(Exception):
    """Stands in for the package's error type, a collaborator like any other."""


@pytest.fixture(autouse=True)
def sandbox_error():
    with patch("agent_harness_sandbox.utils.staged_input.AgentHarnessSandboxError", SandboxError):
        yield


@pytest.fixture
def source(tmp_path):
    directory = tmp_path / "data"
    directory.mkdir()
    return directory


def describe_staged_input():
    def describe_what_it_yields():
        def it_yields_a_directory_of_its_own(source):
            with staged_input(source) as staged:
                assert staged.is_dir()
                assert staged.resolve() != source.resolve()

        def it_holds_the_inputs_files(source):
            (source / "a.txt").write_text("x")
            with staged_input(source) as staged:
                assert (staged / "a.txt").read_text() == "x"

        def it_holds_the_inputs_nested_files(source):
            (source / "nested").mkdir()
            (source / "nested" / "a.txt").write_text("x")
            with staged_input(source) as staged:
                assert (staged / "nested" / "a.txt").read_text() == "x"

        def it_copies_symlinks_as_symlinks(source, tmp_path):
            target = tmp_path / "outside.txt"
            target.write_text("x")
            (source / "link.txt").symlink_to(target)
            with staged_input(source) as staged:
                assert (staged / "link.txt").is_symlink()

        def it_takes_a_string_path(source):
            with staged_input(str(source)) as staged:
                assert isinstance(staged, Path)

    def describe_the_copy():
        def it_keeps_writes_out_of_the_input(source):
            with staged_input(source) as staged:
                (staged / "installed.txt").write_text("from the container")
            assert sorted(p.name for p in source.iterdir()) == []

        def it_discards_the_copy_after_the_block(source):
            with staged_input(source) as staged:
                pass
            assert not staged.exists()

        def it_discards_the_copy_after_an_exception(source):
            with pytest.raises(RuntimeError), staged_input(source) as staged:
                held = staged
                raise RuntimeError("boom")
            assert not held.exists()

    def describe_a_refused_input():
        def it_refuses_an_input_that_is_not_there(tmp_path):
            with pytest.raises(SandboxError, match="does not exist"):
                with staged_input(tmp_path / "gone"):
                    pass

        def it_refuses_an_input_that_is_not_a_folder(tmp_path):
            data = tmp_path / "file"
            data.touch()
            with pytest.raises(SandboxError, match="not a directory"):
                with staged_input(data):
                    pass
