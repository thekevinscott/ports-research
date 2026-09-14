from contamination_probe.rename_symbols import rename_symbols
from contamination_probe.symbol_site import SymbolSite


def make_tree(tmp_path):
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "graph.py").write_text("class Graph:\n    pass\n")
    (package / "user.py").write_text(
        "from .graph import Graph\n\n\ndef make():\n    return Graph()\n"
    )
    return package


def describe_rename_symbols():
    def it_renames_the_definition_site(tmp_path):
        package = make_tree(tmp_path)
        sites = [SymbolSite(path=package / "graph.py", lineno=1, name="Graph")]
        rename_symbols(tmp_path, sites, {"Graph": "Zephyr"})
        assert "class Zephyr:" in (package / "graph.py").read_text()

    def it_renames_the_import_and_usage_sites(tmp_path):
        package = make_tree(tmp_path)
        sites = [SymbolSite(path=package / "graph.py", lineno=1, name="Graph")]
        rename_symbols(tmp_path, sites, {"Graph": "Zephyr"})
        user_source = (package / "user.py").read_text()
        assert "from .graph import Zephyr" in user_source
        assert "return Zephyr()" in user_source

    def it_leaves_names_absent_from_the_rename_map_untouched(tmp_path):
        package = make_tree(tmp_path)
        sites = [SymbolSite(path=package / "graph.py", lineno=1, name="Graph")]
        rename_symbols(tmp_path, sites, {})
        assert "class Graph:" in (package / "graph.py").read_text()

    def it_renames_the_name_inside_an_all_string_literal(tmp_path):
        package = tmp_path / "pkg"
        package.mkdir()
        (package / "graph.py").write_text("class Graph:\n    pass\n")
        (package / "__init__.py").write_text(
            "from .graph import Graph\n\n__all__ = ['Graph']\n"
        )
        sites = [SymbolSite(path=package / "graph.py", lineno=1, name="Graph")]
        rename_symbols(tmp_path, sites, {"Graph": "Zephyr"})
        assert "'Graph'" not in (package / "__init__.py").read_text()
        assert "'Zephyr'" in (package / "__init__.py").read_text()

    def it_renames_every_site_sharing_a_bare_name_exactly_once(tmp_path):
        package = tmp_path / "pkg"
        package.mkdir()
        (package / "__init__.py").write_text("")
        (package / "one.py").write_text("class GraphNode:\n    pass\n")
        (package / "two.py").write_text("class GraphNode:\n    pass\n")
        sites = [
            SymbolSite(path=package / "one.py", lineno=1, name="GraphNode"),
            SymbolSite(path=package / "two.py", lineno=1, name="GraphNode"),
        ]
        rename_symbols(tmp_path, sites, {"GraphNode": "Waypoint"})
        assert "class Waypoint:" in (package / "one.py").read_text()
        assert "class Waypoint:" in (package / "two.py").read_text()
