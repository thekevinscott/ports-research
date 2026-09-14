from pathlib import Path

import pytest

from round_trip_experiment.measure_code_distance import measure_code_distance

FIELDS = {
    "language",
    "a",
    "b",
    "file_count_a",
    "file_count_b",
    "token_count_a",
    "token_count_b",
    "char_count_a",
    "char_count_b",
    "token_levenshtein",
    "token_levenshtein_raw",
    "char_levenshtein",
    "path_count_a",
    "path_count_b",
    "path_levenshtein",
}


def write_tree(root: Path, files: dict[str, str]) -> Path:
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


@pytest.fixture
def a(tmp_path):
    return write_tree(tmp_path / "a", {"pkg/m.py": "x = 1\n", "pkg/n.py": "y = 2\n", "pkg/m_test.py": "z = 3\n"})


def measure(a, b, exclude=["*_test.py"]):
    return measure_code_distance(language="python", a=a, b=b, exclude=exclude)


def describe_measure_code_distance():
    def it_reports_every_field(a):
        assert set(measure(a, a)) == FIELDS

    def it_echoes_language_and_both_paths(a):
        report = measure(a, a)
        assert (report["language"], report["a"], report["b"]) == ("python", str(a), str(a))

    def it_is_zero_for_a_codebase_against_itself(a):
        report = measure(a, a)
        assert (report["token_levenshtein"], report["token_levenshtein_raw"], report["char_levenshtein"]) == (0.0, 0.0, 0.0)

    def it_counts_only_files_the_excludes_keep(a, tmp_path):
        b = write_tree(tmp_path / "b", {"m.py": "x = 1\n"})
        report = measure(a, b)
        assert (report["file_count_a"], report["file_count_b"]) == (2, 1)

    def it_counts_tokens_and_characters_over_the_kept_files(a):
        report = measure(a, a)
        assert (report["token_count_a"], report["char_count_a"]) == (6, 12)

    def it_ignores_identifier_renames_in_the_abstracted_token_distance(a, tmp_path):
        b = write_tree(tmp_path / "b", {"pkg/m.py": "p = 1\n", "pkg/n.py": "q = 2\n"})
        report = measure(a, b)
        assert report["token_levenshtein"] == 0.0
        assert report["token_levenshtein_raw"] == pytest.approx(2 / 6)

    def it_sees_literal_changes_in_both_token_distances(a, tmp_path):
        b = write_tree(tmp_path / "b", {"pkg/m.py": "x = 9\n", "pkg/n.py": "y = 2\n"})
        report = measure(a, b)
        assert report["token_levenshtein"] == pytest.approx(1 / 6)
        assert report["token_levenshtein_raw"] == pytest.approx(1 / 6)

    def it_measures_character_distance_over_the_concatenated_text(a, tmp_path):
        b = write_tree(tmp_path / "b", {"pkg/m.py": "x = 1\n", "pkg/n.py": "y = 22\n"})
        assert measure(a, b)["char_levenshtein"] == pytest.approx(1 / 13)

    def it_concatenates_files_in_sorted_relative_path_order(a, tmp_path):
        b = write_tree(tmp_path / "b", {"pkg/a.py": "x = 1\ny = 2\n"})
        assert measure(a, b)["char_levenshtein"] == 0.0

    def it_fails_when_a_side_has_no_source_files(a, tmp_path):
        b = write_tree(tmp_path / "b", {"notes.md": "not code"})
        with pytest.raises(FileNotFoundError, match="no python source"):
            measure(a, b)

    def it_counts_every_file_the_excludes_keep_as_a_path(a, tmp_path):
        b = write_tree(tmp_path / "b", {"m.py": "x = 1\n", "notes.md": "not code"})
        report = measure(a, b)
        assert (report["path_count_a"], report["path_count_b"]) == (2, 2)

    def it_has_zero_path_distance_for_a_codebase_against_itself(a):
        assert measure(a, a)["path_levenshtein"] == 0.0

    def it_counts_a_rename_in_a_nested_directory_as_one_path_edit(a, tmp_path):
        b = write_tree(tmp_path / "b", {"pkg/m.py": "x = 1\n", "pkg/o.py": "y = 2\n"})
        assert measure(a, b)["path_levenshtein"] == pytest.approx(1 / 2)

    def it_counts_an_added_file_of_any_kind_as_one_path_edit(a, tmp_path):
        b = write_tree(tmp_path / "b", {"pkg/m.py": "x = 1\n", "pkg/n.py": "y = 2\n", "pkg/notes.md": "not code"})
        assert measure(a, b)["path_levenshtein"] == pytest.approx(1 / 3)

    def it_counts_every_file_moved_into_another_directory_as_a_path_edit(a, tmp_path):
        b = write_tree(tmp_path / "b", {"lib/m.py": "x = 1\n", "lib/n.py": "y = 2\n"})
        assert measure(a, b)["path_levenshtein"] == 1.0

    def it_measures_typescript_with_the_typescript_grammar(tmp_path):
        a = write_tree(tmp_path / "a", {"s.ts": "const a: Foo = 1;\n"})
        b = write_tree(tmp_path / "b", {"s.ts": "const b: Bar = 1;\n"})
        report = measure_code_distance(language="typescript", a=a, b=b, exclude=[])
        assert report["token_levenshtein"] == 0.0
        assert report["token_levenshtein_raw"] == pytest.approx(2 / 7)
