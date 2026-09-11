from contamination_probe.discover_modules import discover_modules


def write(path, text):
    path.write_text(text)
    return path


def describe_discover_modules():
    def it_finds_a_top_level_module(tmp_path):
        write(tmp_path / "graph.py", "class Graph:\n    pass\n")
        assert discover_modules(tmp_path) == [tmp_path / "graph.py"]

    def it_skips_init_files(tmp_path):
        write(tmp_path / "__init__.py", "")
        write(tmp_path / "graph.py", "class Graph:\n    pass\n")
        assert discover_modules(tmp_path) == [tmp_path / "graph.py"]

    def it_skips_colocated_test_files(tmp_path):
        write(tmp_path / "graph.py", "class Graph:\n    pass\n")
        write(tmp_path / "graph_test.py", "class Graph:\n    pass\n")
        assert discover_modules(tmp_path) == [tmp_path / "graph.py"]

    def it_recurses_into_subdirectories(tmp_path):
        nested = tmp_path / "grammar_graph"
        nested.mkdir()
        write(nested / "types.py", "class RuleChar:\n    pass\n")
        assert discover_modules(tmp_path) == [nested / "types.py"]

    def it_sorts_results_by_path(tmp_path):
        write(tmp_path / "b.py", "class B:\n    pass\n")
        write(tmp_path / "a.py", "class A:\n    pass\n")
        assert [path.name for path in discover_modules(tmp_path)] == ["a.py", "b.py"]
