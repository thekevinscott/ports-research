from judge.code_item import code_item


def tree(root, files):
    for relative, text in files.items():
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text(text)
    return root


def describe_code_item():
    def it_concatenates_side_a_then_side_b_each_file_under_its_path_with_numbered_lines(tmp_path):
        a = tree(tmp_path / "a", {"pkg/m.py": "x = 1\ny = 2\n", "pkg/m_test.py": "assert x\n"})
        b = tree(tmp_path / "b", {"src/m.ts": "export const x = 1;\n"})
        assert code_item(a, b) == (
            "# Side A\n\n"
            "=== A: pkg/m.py ===\n"
            "1| x = 1\n"
            "2| y = 2\n"
            "\n"
            "# Side B\n\n"
            "=== B: src/m.ts ===\n"
            "1| export const x = 1;\n"
        )

    def it_names_no_path_outside_the_two_trees(tmp_path):
        a = tree(tmp_path / "20261012T000000Z_abcdef12" / "ported_implementation", {"m.py": "x = 1\n"})
        b = tree(tmp_path / "gbnf" / "javascript", {"m.ts": "x\n"})
        item = code_item(a, b)
        assert str(tmp_path) not in item
        assert "abcdef12" not in item
        assert "ported_implementation" not in item
