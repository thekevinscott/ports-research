from contamination_probe.discover_public_symbols import discover_public_symbols
from contamination_probe.symbol_site import SymbolSite


def write(path, text):
    path.write_text(text)
    return path


def describe_discover_public_symbols():
    def it_finds_a_top_level_class(tmp_path):
        write(tmp_path / "graph.py", "class Graph:\n    pass\n")
        sites = discover_public_symbols(tmp_path)
        assert sites == [SymbolSite(path=tmp_path / "graph.py", lineno=1, name="Graph")]

    def it_finds_a_top_level_function(tmp_path):
        write(tmp_path / "helpers.py", "def is_point_in_range():\n    pass\n")
        sites = discover_public_symbols(tmp_path)
        assert sites == [
            SymbolSite(path=tmp_path / "helpers.py", lineno=1, name="is_point_in_range")
        ]

    def it_finds_a_top_level_constant_assignment(tmp_path):
        write(tmp_path / "types.py", "RootNode = dict[int, str]\n")
        sites = discover_public_symbols(tmp_path)
        assert sites == [
            SymbolSite(path=tmp_path / "types.py", lineno=1, name="RootNode")
        ]

    def it_skips_names_starting_with_underscore(tmp_path):
        write(tmp_path / "graph.py", "class _Internal:\n    pass\n\ndef _helper():\n    pass\n")
        assert discover_public_symbols(tmp_path) == []

    def it_skips_typevar_assignments(tmp_path):
        write(tmp_path / "types.py", "from typing import TypeVar\n\nT = TypeVar('T')\n")
        assert discover_public_symbols(tmp_path) == []

    def it_skips_multi_target_assignments(tmp_path):
        write(tmp_path / "module.py", "A = B = 1\n")
        assert discover_public_symbols(tmp_path) == []

    def it_skips_colocated_test_files(tmp_path):
        write(tmp_path / "graph.py", "class Graph:\n    pass\n")
        write(tmp_path / "graph_test.py", "class Graph:\n    pass\n")
        sites = discover_public_symbols(tmp_path)
        assert sites == [SymbolSite(path=tmp_path / "graph.py", lineno=1, name="Graph")]

    def it_recurses_into_subdirectories(tmp_path):
        nested = tmp_path / "grammar_graph"
        nested.mkdir()
        write(nested / "graph.py", "class Graph:\n    pass\n")
        sites = discover_public_symbols(tmp_path)
        assert sites == [SymbolSite(path=nested / "graph.py", lineno=1, name="Graph")]

    def it_sorts_results_by_path(tmp_path):
        write(tmp_path / "b.py", "class B:\n    pass\n")
        write(tmp_path / "a.py", "class A:\n    pass\n")
        sites = discover_public_symbols(tmp_path)
        assert [site.path.name for site in sites] == ["a.py", "b.py"]
