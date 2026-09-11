"""Materialise a runnable copy of the TypeScript reference implementation.

Node 24 can execute TypeScript directly with ``--experimental-transform-types``, but
its per-file transform (no type information) needs two things the reference sources
don't provide:

* import specifiers that resolve to files that exist on disk (the sources import
  ``./foo.js`` while shipping ``./foo.ts``);
* ``import type`` markers on type-only imports.

Both are applied here to a scratch copy; the reference tree itself is never modified
(it is mounted read-only anyway).
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

REFERENCE_SRC = Path("/workspace/reference_implementation/src")

# Names exported as types only; they must be imported with `import type` for Node's
# type-stripping transform to erase them.
TYPE_ONLY_EXPORTS = {
    "InternalRuleDef",
    "InternalRuleDefWithNumericValue",
    "InternalRuleDefChar",
    "InternalRuleDefCharNot",
    "InternalRuleDefCharAlt",
    "InternalRuleDefReference",
    "InternalRuleDefEnd",
    "InternalRuleDefWithoutValue",
    "InternalRuleDefCharOrAltChar",
    "Pointers",
    "PrintOpts",
    "Range",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "UnresolvedRule",
    "ResolvedRule",
    "ResolvedGraphPointer",
    "ValidInput",
    "Colorize",
    "GraphNodeRuleRef",
    "GraphPointerKey",
}


def _fix_import_clause(match: "re.Match[str]") -> str:
    parts = []
    for raw in match.group(1).split(","):
        spec = raw.strip()
        if not spec:
            continue
        name = spec.split()[-1].split(" as ")[0].strip()
        if name in TYPE_ONLY_EXPORTS and not spec.startswith("type "):
            spec = "type " + spec
        parts.append(spec)
    return "{ " + ", ".join(parts) + " }"


def prepare(target: Path, reference_src: Path = REFERENCE_SRC) -> Path:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(reference_src, target)

    for path in target.rglob("*.ts"):
        src = path.read_text()
        # ./foo.js -> ./foo.ts
        src = re.sub(r"""(from\s+["'][^"']*)\.js(["'])""", r"\1.ts\2", src)
        # add `type` to type-only named imports
        src = re.sub(r"\{([^{}]*)\}(?=\s*from)", _fix_import_clause, src)
        # ... but `import type { A, B }` may not carry per-name `type` markers
        src = re.sub(
            r"(import\s+type\s*\{)([^{}]*)(\})",
            lambda m: m.group(1) + m.group(2).replace("type ", "") + m.group(3),
            src,
        )
        path.write_text(src)

    # `src/builder/gbnf-rule` does not exist in the reference tree; the import is used
    # only for a type annotation on the GBNF() input parameter.
    gbnf = target / "gbnf.ts"
    text = gbnf.read_text()
    text = "\n".join(
        line for line in text.splitlines() if "builder/gbnf-rule" not in line
    )
    text = text.replace("input: string | GBNFRule", "input: string")
    gbnf.write_text(text)

    return target


def node_version() -> Optional[str]:
    try:
        out = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None
