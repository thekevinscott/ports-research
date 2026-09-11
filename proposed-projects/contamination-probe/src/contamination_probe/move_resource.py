from pathlib import Path

from rope.base.project import Project
from rope.refactor.move import MoveModule


def move_resource(project: Project, project_root: Path, source_path: Path, dest_dir: Path) -> None:
    """Moves `source_path` into `dest_dir` via rope, normalizing its own relative imports first.

    Raises rather than silently overwriting if a file of the same name already exists at
    `dest_dir`: rope's own move clobbers in that case, which would lose a file rather than
    merely relocate it.
    """
    if (dest_dir / source_path.name).exists():
        raise ValueError(f"reshuffle would overwrite {dest_dir / source_path.name}")
    resource = project.get_resource(str(source_path.relative_to(project_root)))
    dest = project.get_resource(str(dest_dir.relative_to(project_root)))
    project.do(MoveModule(project, resource).get_changes(dest))
