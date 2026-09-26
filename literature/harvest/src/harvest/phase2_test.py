import importlib
import os

import pytest

from harvest import phase2
from harvest.phase2 import norm, references_section, seeds, split_entries


def describe_import():
    def it_does_not_touch_the_filesystem(tmp_path, monkeypatch):
        # Regression: the module used to build its seed set at import time, so importing it
        # anywhere without a papers/ directory raised FileNotFoundError.
        monkeypatch.chdir(tmp_path)
        importlib.reload(phase2)
        assert not os.listdir(tmp_path)


def describe_seeds():
    def it_reads_the_corpus_only_when_called(tmp_path):
        (tmp_path / "alpha").mkdir()
        (tmp_path / "alpha" / "paper.md").write_text("x")
        (tmp_path / "beta").mkdir()
        assert seeds(tmp_path) == {"alpha"}

    def it_raises_on_a_missing_corpus(tmp_path):
        with pytest.raises(FileNotFoundError):
            seeds(tmp_path / "absent")


def describe_references_section():
    def it_returns_empty_when_there_is_no_heading():
        assert references_section("no heading here") == ""


def describe_split_entries():
    def it_joins_continuation_lines_into_one_entry():
        section = "- Smith and Jones, A study of something reasonably long\n  in two parts\n"
        assert split_entries(section) == [
            "- Smith and Jones, A study of something reasonably long in two parts"
        ]

    def it_drops_entries_shorter_than_thirty_characters():
        assert split_entries("- too short\n") == []


def describe_norm():
    def it_lowercases_and_collapses_punctuation():
        assert norm("Lost in Translation: A Study!") == "lost in translation a study"
