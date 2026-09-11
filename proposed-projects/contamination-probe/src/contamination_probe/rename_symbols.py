from pathlib import Path

from rope.base.project import Project
from rope.refactor.rename import Rename

from .locate_name_offset import locate_name_offset
from .symbol_site import SymbolSite


def rename_symbols(
    project_root: Path, sites: list[SymbolSite], rename_map: dict[str, str]
) -> None:
    """Renames every symbol in `rename_map`, project-wide, in place under `project_root`.

    Each definition site is renamed from its own offset — rope resolves and propagates
    that rename only across the imports and usages actually connected to it, including
    test files. Two unrelated definitions that happen to share a bare name (independent
    classes, each locally named e.g. `GraphNode`) are renamed by two separate calls;
    since `rename_map` is keyed by bare name, both still land on the same new name.

    Renaming through string substitution was ruled out deliberately: it can't tell a
    definition from an unrelated identical substring, and it can't follow rope's
    relative-import resolution across files. rope was chosen over libcst here because
    libcst's built-in `RenameCommand` resolves only module-local qualified names and
    can't follow this codebase's relative imports; it would silently rename nothing.

    `docs=True` extends the rename into comments and string literals where the name is
    visible — needed because `gbnf`'s own `__init__.py` re-exports through a plain
    `__all__ = ["GBNF", ...]` list, which is a string, not a reference an AST-only
    rename would touch.
    """
    project = Project(str(project_root))
    renamed_sites: set[tuple[Path, int, str]] = set()
    try:
        for site in sites:
            key = (site.path, site.lineno, site.name)
            if key in renamed_sites or site.name not in rename_map:
                continue
            renamed_sites.add(key)
            resource = project.get_resource(str(site.path.relative_to(project_root)))
            offset = locate_name_offset(resource.read(), site.lineno, site.name)
            changes = Rename(project, resource, offset).get_changes(
                rename_map[site.name], docs=True
            )
            project.do(changes)
    finally:
        project.close()
