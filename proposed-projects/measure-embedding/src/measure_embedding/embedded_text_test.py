import pytest

from measure_embedding.embedded_text import embedded_text

SOURCE = b"a = 1  # note\n"


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "a.py"
    path.write_bytes(SOURCE)
    return path


def describe_embedded_text():
    def it_returns_the_file_unchanged_when_not_stripping(source):
        assert embedded_text(source, "python", False) == SOURCE

    def it_returns_the_file_without_its_comments_when_stripping(source):
        assert embedded_text(source, "python", True) == b"a = 1  \n"
