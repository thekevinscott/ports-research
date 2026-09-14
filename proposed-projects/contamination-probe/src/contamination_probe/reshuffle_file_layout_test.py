import pytest

from contamination_probe.discover_modules import discover_modules
from contamination_probe.reshuffle_file_layout import reshuffle_file_layout


def write_nested_library(tmp_path):
    library_root = tmp_path / "gbnf"
    sub = library_root / "grammar_graph"
    sub.mkdir(parents=True)
    (library_root / "__init__.py").write_text(
        "from .grammar_graph.a_mod import A\nfrom .grammar_graph.b_mod import B\n\n"
        "__all__ = ['A', 'B']\n"
    )
    (sub / "__init__.py").write_text("")
    (sub / "a_mod.py").write_text("class A:\n    pass\n")
    (sub / "b_mod.py").write_text("from .a_mod import A\n\n\nclass B(A):\n    pass\n")
    (sub / "a_mod_test.py").write_text("from .a_mod import A\n\n\ndef test_a():\n    assert A()\n")
    (sub / "b_mod_test.py").write_text("from .b_mod import B\n\n\ndef test_b():\n    assert B()\n")
    return library_root


def write_library_with_a_test_helper_import(tmp_path):
    library_root = tmp_path / "gbnf"
    sub = library_root / "grammar_graph"
    sub.mkdir(parents=True)
    (library_root / "__init__.py").write_text("")
    (sub / "__init__.py").write_text("")
    (sub / "mod_a.py").write_text("class A:\n    pass\n")
    (sub / "mod_b.py").write_text("class B:\n    pass\n")
    (sub / "mod_a_test.py").write_text(
        "from .mod_a import A\nfrom .mod_b import B\n\n\ndef test_a():\n    assert A() and B()\n"
    )
    return library_root


def describe_reshuffle_file_layout():
    def it_moves_modules_out_of_their_original_directory(tmp_path):
        library_root = write_nested_library(tmp_path)
        reshuffle_file_layout(library_root, seed=0)
        assert not (library_root / "grammar_graph" / "a_mod.py").exists()
        assert not (library_root / "grammar_graph" / "b_mod.py").exists()

    def it_moves_each_colocated_test_alongside_its_module(tmp_path):
        library_root = write_nested_library(tmp_path)
        reshuffle_file_layout(library_root, seed=0)
        for module_path in discover_modules(library_root):
            test_path = module_path.with_name(module_path.stem + "_test.py")
            assert test_path.exists()

    def it_fixes_up_imports_so_the_barrel_still_resolves(tmp_path):
        library_root = write_nested_library(tmp_path)
        reshuffle_file_layout(library_root, seed=0)
        init_source = (library_root / "__init__.py").read_text()
        assert "grammar_graph" not in init_source

    def it_fixes_up_cross_module_imports(tmp_path):
        library_root = write_nested_library(tmp_path)
        reshuffle_file_layout(library_root, seed=0)
        [b_mod_path] = [p for p in discover_modules(library_root) if p.name == "b_mod.py"]
        assert "from .a_mod import A" not in b_mod_path.read_text()

    def it_is_deterministic_for_a_given_seed(tmp_path):
        first_root = write_nested_library(tmp_path / "first")
        second_root = write_nested_library(tmp_path / "second")
        reshuffle_file_layout(first_root, seed=0)
        reshuffle_file_layout(second_root, seed=0)
        first_layout = {p.relative_to(first_root) for p in discover_modules(first_root)}
        second_layout = {p.relative_to(second_root) for p in discover_modules(second_root)}
        assert first_layout == second_layout

    def it_raises_rather_than_silently_overwriting_a_name_collision(tmp_path):
        library_root = tmp_path / "gbnf"
        dir_a = library_root / "dir_a"
        dir_b = library_root / "dir_b"
        dir_a.mkdir(parents=True)
        dir_b.mkdir(parents=True)
        (library_root / "__init__.py").write_text("")
        (dir_a / "__init__.py").write_text("")
        (dir_b / "__init__.py").write_text("")
        (dir_a / "state.py").write_text("class StateA:\n    pass\n")
        (dir_b / "state.py").write_text("class StateB:\n    pass\n")

        with pytest.raises(ValueError, match="state.py"):
            reshuffle_file_layout(library_root, seed=0, bucket_count=1)

    def it_fixes_a_test_files_import_of_a_sibling_helper_moved_to_another_bucket(tmp_path):
        library_root = write_library_with_a_test_helper_import(tmp_path)

        reshuffle_file_layout(library_root, seed=1, bucket_count=2)

        [test_path] = [
            p for p in library_root.rglob("mod_a_test.py")
        ]
        [b_mod_path] = [p for p in discover_modules(library_root) if p.name == "mod_b.py"]
        assert test_path.parent != b_mod_path.parent
        assert "from .mod_b import B" not in test_path.read_text()
