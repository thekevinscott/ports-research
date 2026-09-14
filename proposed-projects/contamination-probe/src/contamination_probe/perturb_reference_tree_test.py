import json

from contamination_probe.discover_modules import discover_modules
from contamination_probe.perturb_reference_tree import perturb_reference_tree


def make_source_tree(tmp_path):
    source = tmp_path / "source"
    package = source / "gbnf"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("from .graph import Graph\n\n__all__ = ['Graph']\n")
    (package / "graph.py").write_text("class Graph:\n    pass\n")
    (package / "graph_test.py").write_text(
        "from .graph import Graph\n\n\ndef test_it_constructs():\n    assert Graph()\n"
    )
    (source / "pyproject.toml").write_text('[project]\nname = "gbnf"\n')
    (source / "README.md").write_text("# gbnf\n")
    return source


def describe_perturb_reference_tree():
    def it_returns_a_new_library_name_that_differs_from_the_original(tmp_path):
        source = make_source_tree(tmp_path)
        new_name = perturb_reference_tree(
            source, tmp_path / "output", library_name="gbnf", seed=0
        )
        assert new_name != "gbnf"

    def it_renames_the_library_directory_in_the_output_tree(tmp_path):
        source = make_source_tree(tmp_path)
        output = tmp_path / "output"
        new_name = perturb_reference_tree(source, output, library_name="gbnf", seed=0)
        assert not (output / "gbnf").exists()
        assert (output / new_name).is_dir()

    def it_rewrites_the_library_name_in_pyproject_toml(tmp_path):
        source = make_source_tree(tmp_path)
        output = tmp_path / "output"
        new_name = perturb_reference_tree(source, output, library_name="gbnf", seed=0)
        assert f'name = "{new_name}"' in (output / "pyproject.toml").read_text()

    def it_leaves_the_source_tree_untouched(tmp_path):
        source = make_source_tree(tmp_path)
        perturb_reference_tree(source, tmp_path / "output", library_name="gbnf", seed=0)
        assert (source / "gbnf" / "graph.py").read_text() == "class Graph:\n    pass\n"

    def it_is_deterministic_for_a_given_seed(tmp_path):
        source = make_source_tree(tmp_path)
        first = perturb_reference_tree(
            source, tmp_path / "output1", library_name="gbnf", seed=0
        )
        second = perturb_reference_tree(
            source, tmp_path / "output2", library_name="gbnf", seed=0
        )
        assert first == second

    def it_varies_the_new_library_name_with_seed(tmp_path):
        source = make_source_tree(tmp_path)
        first = perturb_reference_tree(
            source, tmp_path / "output1", library_name="gbnf", seed=0
        )
        second = perturb_reference_tree(
            source, tmp_path / "output2", library_name="gbnf", seed=1
        )
        assert first != second

    def it_renames_the_public_class_consistently_across_definition_and_test(tmp_path):
        source = make_source_tree(tmp_path)
        output = tmp_path / "output"
        new_library_name = perturb_reference_tree(
            source, output, library_name="gbnf", seed=0
        )
        [graph_path] = [
            path
            for path in discover_modules(output / new_library_name)
            if path.name.startswith("graph")
        ]
        graph_source = graph_path.read_text()
        assert "class Graph:" not in graph_source
        new_class_name = graph_source.split("class ")[1].split(":")[0].split("(")[0]

        init_source = (output / new_library_name / "__init__.py").read_text()
        assert new_class_name in init_source
        assert "Graph" not in init_source

        test_source = graph_path.with_name(graph_path.stem + "_test.py").read_text()
        assert new_class_name in test_source
        assert "Graph" not in test_source

    def it_moves_modules_out_of_their_original_directory(tmp_path):
        source = make_source_tree(tmp_path)
        output = tmp_path / "output"
        new_library_name = perturb_reference_tree(
            source, output, library_name="gbnf", seed=0
        )
        assert not (output / new_library_name / "graph.py").exists()

    def it_writes_a_rename_manifest_a_grading_suite_can_be_ported_through(tmp_path):
        source = make_source_tree(tmp_path)
        output = tmp_path / "output"
        new_library_name = perturb_reference_tree(
            source, output, library_name="gbnf", seed=0
        )
        manifest = json.loads((output / "rename-manifest.json").read_text())
        assert manifest["library_name"] == {"old": "gbnf", "new": new_library_name}
        assert "Graph" in manifest["symbols"]
