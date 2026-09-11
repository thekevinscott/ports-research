from contamination_probe.rename_library import rename_library


def describe_rename_library():
    def it_renames_the_package_directory(tmp_path):
        (tmp_path / "gbnf").mkdir()
        (tmp_path / "gbnf" / "__init__.py").write_text("")
        rename_library(tmp_path, "gbnf", "lattice")
        assert not (tmp_path / "gbnf").exists()
        assert (tmp_path / "lattice" / "__init__.py").exists()

    def it_rewrites_the_name_in_pyproject_toml(tmp_path):
        (tmp_path / "gbnf").mkdir()
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "gbnf"\n\n[tool.setuptools.packages.find]\ninclude = ["gbnf*"]\n'
        )
        rename_library(tmp_path, "gbnf", "lattice")
        text = (tmp_path / "pyproject.toml").read_text()
        assert 'name = "lattice"' in text
        assert 'include = ["lattice*"]' in text
        assert "gbnf" not in text

    def it_rewrites_the_name_in_the_readme(tmp_path):
        (tmp_path / "gbnf").mkdir()
        (tmp_path / "README.md").write_text("# gbnf\n\nA gbnf grammar library.\n")
        rename_library(tmp_path, "gbnf", "lattice")
        text = (tmp_path / "README.md").read_text()
        assert "lattice" in text
        assert "gbnf" not in text

    def it_is_a_no_op_for_metadata_files_that_do_not_exist(tmp_path):
        (tmp_path / "gbnf").mkdir()
        rename_library(tmp_path, "gbnf", "lattice")
        assert (tmp_path / "lattice").exists()

    def it_replaces_every_occurrence_on_a_line(tmp_path):
        (tmp_path / "gbnf").mkdir()
        (tmp_path / "README.md").write_text("gbnf/gbnf: a gbnf grammar library\n")
        rename_library(tmp_path, "gbnf", "lattice")
        text = (tmp_path / "README.md").read_text()
        assert text == "lattice/lattice: a lattice grammar library\n"
