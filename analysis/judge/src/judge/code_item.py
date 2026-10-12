from pathlib import Path

from judge.source_files import source_files


def code_item(a: Path, b: Path) -> str:
    """Side A then side B, each file under its relative path, each line numbered."""

    def side(name: str, root: Path) -> str:
        files = []
        for relative in source_files(root):
            lines = (root / relative).read_text(errors="replace").splitlines()
            numbered = "".join(f"{n}| {line}\n" for n, line in enumerate(lines, 1))
            files.append(f"=== {name}: {relative.as_posix()} ===\n{numbered}")
        return f"# Side {name}\n\n" + "\n".join(files)

    return side("A", a) + "\n" + side("B", b)
