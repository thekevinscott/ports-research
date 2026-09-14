import pytest
from rope.base.project import Project

from contamination_probe.move_resource import move_resource


def describe_move_resource():
    def it_relocates_the_file_into_the_destination_directory(tmp_path):
        root = tmp_path / "gbnf"
        dest = root / "dest"
        root.mkdir()
        dest.mkdir()
        (root / "__init__.py").write_text("")
        (dest / "__init__.py").write_text("")
        (root / "mod.py").write_text("class A:\n    pass\n")

        project = Project(str(tmp_path))
        try:
            move_resource(project, tmp_path, root / "mod.py", dest)
        finally:
            project.close()

        assert not (root / "mod.py").exists()
        assert (dest / "mod.py").exists()

    def it_normalizes_the_moving_files_own_relative_imports(tmp_path):
        root = tmp_path / "gbnf"
        dest = root / "dest"
        root.mkdir()
        dest.mkdir()
        (root / "__init__.py").write_text("")
        (dest / "__init__.py").write_text("")
        (root / "helper.py").write_text("class Helper:\n    pass\n")
        (root / "mod.py").write_text("from .helper import Helper\n\n\nclass A(Helper):\n    pass\n")

        project = Project(str(tmp_path))
        try:
            move_resource(project, tmp_path, root / "mod.py", dest)
        finally:
            project.close()

        assert "from .helper import Helper" not in (dest / "mod.py").read_text()

    def it_raises_rather_than_silently_overwriting_a_name_collision(tmp_path):
        root = tmp_path / "gbnf"
        dest = root / "dest"
        root.mkdir()
        dest.mkdir()
        (root / "__init__.py").write_text("")
        (dest / "__init__.py").write_text("")
        (root / "mod.py").write_text("class A:\n    pass\n")
        (dest / "mod.py").write_text("class AlreadyThere:\n    pass\n")

        project = Project(str(tmp_path))
        try:
            with pytest.raises(ValueError, match="mod.py"):
                move_resource(project, tmp_path, root / "mod.py", dest)
        finally:
            project.close()
