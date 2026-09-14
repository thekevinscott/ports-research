import json

from click.testing import CliRunner

from contamination_probe.cli import cli
from contamination_probe.discover_modules import discover_modules


def write_reference_tree(tmp_path):
    source = tmp_path / "source"
    package = source / "gbnf"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("from .graph import Graph\n\n__all__ = ['Graph']\n")
    (package / "graph.py").write_text("class Graph:\n    pass\n")
    (source / "pyproject.toml").write_text('[project]\nname = "gbnf"\n')
    return source


def invoke(source, output, seed=0):
    return CliRunner().invoke(
        cli,
        [
            "--source", str(source),
            "--output", str(output),
            "--library-name", "gbnf",
            "--seed", str(seed),
        ],
    )


def describe_cli():
    def it_produces_a_perturbed_tree_with_the_library_renamed(tmp_path):
        source = write_reference_tree(tmp_path)
        output = tmp_path / "output"

        result = invoke(source, output)

        assert result.exit_code == 0
        new_library_name = json.loads(result.output)["library_name"]
        assert new_library_name != "gbnf"
        assert not (output / "gbnf").exists()
        assert (output / new_library_name).is_dir()
        assert f'name = "{new_library_name}"' in (output / "pyproject.toml").read_text()

    def it_is_reproducible_for_the_same_seed(tmp_path):
        source = write_reference_tree(tmp_path)

        first = invoke(source, tmp_path / "output1")
        second = invoke(source, tmp_path / "output2")

        assert json.loads(first.output)["library_name"] == json.loads(second.output)[
            "library_name"
        ]

    def it_renames_the_public_class_everywhere_it_appears(tmp_path):
        source = write_reference_tree(tmp_path)
        output = tmp_path / "output"

        result = invoke(source, output)

        new_library_name = json.loads(result.output)["library_name"]
        [graph_path] = [
            path
            for path in discover_modules(output / new_library_name)
            if path.name.startswith("graph")
        ]
        graph_source = graph_path.read_text()
        assert "class Graph:" not in graph_source
        new_class_name = graph_source.split("class ")[1].split(":")[0]

        init_source = (output / new_library_name / "__init__.py").read_text()
        assert new_class_name in init_source
        assert "Graph" not in init_source

    def it_reshuffles_the_file_layout(tmp_path):
        source = write_reference_tree(tmp_path)
        output = tmp_path / "output"

        result = invoke(source, output)

        new_library_name = json.loads(result.output)["library_name"]
        assert not (output / new_library_name / "graph.py").exists()
