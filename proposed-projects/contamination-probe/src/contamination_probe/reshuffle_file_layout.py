from pathlib import Path
from random import Random

from rope.base.project import Project

from .discover_modules import discover_modules
from .generate_synthetic_name import generate_synthetic_name
from .move_resource import move_resource


def reshuffle_file_layout(library_root: Path, *, seed: int, bucket_count: int = 4) -> None:
    """Distributes every module under `library_root` across newly named sibling packages.

    Both a module and its colocated test are moved through rope's own MoveModule, not a
    plain filesystem move: a test file may import a sibling helper besides the module it
    tests, and only rope's own move normalizes *all* of a moving file's own relative
    imports against its old location before relocating it. A plain move leaves such a
    reference stale — a real failure this package hit against the actual gbnf tree,
    where a test importing a second sibling module broke once that sibling moved to a
    different bucket than the test itself.
    """
    rng = Random(seed)
    bucket_names = [generate_synthetic_name(f"bucket{i}", rng) for i in range(bucket_count)]

    project = Project(str(library_root.parent))
    try:
        bucket_dirs = {}
        for name in bucket_names:
            bucket_dir = library_root / name
            bucket_dir.mkdir(exist_ok=True)
            (bucket_dir / "__init__.py").touch(exist_ok=True)
            bucket_dirs[name] = bucket_dir

        for module_path in discover_modules(library_root):
            bucket_dir = bucket_dirs[rng.choice(bucket_names)]
            move_resource(project, library_root.parent, module_path, bucket_dir)

            test_path = module_path.with_name(module_path.stem + "_test.py")
            if test_path.exists():
                move_resource(project, library_root.parent, test_path, bucket_dir)
    finally:
        project.close()
