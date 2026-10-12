from pathlib import Path

import pytest

from measure_ast.parse_files import parse_files


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    (tmp_path / "a.py").write_bytes(b"x = 1\n")
    (tmp_path / "a_test.py").write_bytes(b"y = 2\n")
    (tmp_path / "b.ts").write_bytes(b"const z = 3;\n")
    (tmp_path / "c.tsx").write_bytes(b"const w = <div />;\n")
    return tmp_path


def describe_parse_files():
    def it_parses_the_language_files_left_after_exclusion(tree):
        trees = parse_files(language="python", target=tree, exclude=["*_test.py"])
        assert [t.root_node.text for t in trees] == [b"x = 1\n"]

    def it_parses_tsx_with_the_tsx_grammar(tree):
        trees = parse_files(language="typescript", target=tree, exclude=[])
        assert [t.root_node.has_error for t in trees] == [False, False]

    def it_raises_when_no_file_parsed(tmp_path):
        with pytest.raises(FileNotFoundError, match="no python source"):
            parse_files(language="python", target=tmp_path, exclude=[])
