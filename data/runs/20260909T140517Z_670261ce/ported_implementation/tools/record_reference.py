"""Record the reference implementation's output for the shared corpus.

Runs ``reference_implementation`` (Typescript) under Node's type-stripping mode
over every case in ``tests/cases.py`` and writes the result to
``tests/fixtures/reference.json``, which ``tests/test_parity.py`` then checks the
Python port against. Node is only needed to *record* the fixtures; running the
tests does not need it.

Usage:  python3 ported_implementation/tools/record_reference.py
"""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "reference_implementation"
FIXTURES = ROOT / "ported_implementation" / "tests" / "fixtures"

sys.path.insert(0, str(ROOT / "ported_implementation" / "tests"))
from cases import CASES  # noqa: E402

# `src/builder/` is not part of the provided reference snapshot; `gbnf.ts` only uses
# it for a type and a `toString()` call.
BUILDER_STUB = """
export class GBNFRule {
  toString(): string { return ''; }
}
"""

# Node strips types rather than compiling them, so it cannot tell that a named
# import is a type; these have to be marked explicitly.
TYPE_ONLY_EXPORTS = {
    "Colorize",
    "InternalRuleDef",
    "InternalRuleDefChar",
    "InternalRuleDefCharAlt",
    "InternalRuleDefCharNot",
    "InternalRuleDefCharOrAltChar",
    "InternalRuleDefEnd",
    "InternalRuleDefReference",
    "InternalRuleDefWithNumericValue",
    "InternalRuleDefWithoutValue",
    "Pointers",
    "PrintOpts",
    "Range",
    "ResolvedGraphPointer",
    "ResolvedRule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "UnresolvedRule",
    "ValidInput",
}

# Node does not resolve the `.js` specifiers of a Typescript source tree to `.ts`.
RESOLVE_HOOK = """
import { registerHooks } from 'node:module';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

registerHooks({
  resolve(specifier, context, nextResolve) {
    if (/^\\.{1,2}\\//.test(specifier) && specifier.endsWith('.js') && context.parentURL) {
      const ts = fileURLToPath(new URL(specifier, context.parentURL)).replace(/\\.js$/, '.ts');
      if (existsSync(ts)) {
        return nextResolve(specifier.replace(/\\.js$/, '.ts'), context);
      }
    }
    return nextResolve(specifier, context);
  },
});
"""

HARNESS = """
import { GBNF } from './src/gbnf.js';
import { readFileSync } from 'node:fs';

const serialize = (rule: any) => (
  rule.type === 'end' ? { type: rule.type } : { type: rule.type, value: rule.value }
);

const cases = JSON.parse(readFileSync(process.argv[2], 'utf-8'));
const results = cases.map((testCase: any) => {
  try {
    let state = GBNF(testCase.grammar, testCase.initial ?? '');
    const steps: any[] = [[...state].map(serialize)];
    for (const chunk of (testCase.adds ?? [])) {
      state = state.add(chunk);
      steps.push([...state].map(serialize));
    }
    return { name: testCase.name, ok: true, steps, size: state.size, grammar: state.grammar };
  } catch (err: any) {
    return { name: testCase.name, ok: false, error: err.name, message: err.message };
  }
});
console.log(JSON.stringify(results, null, 2));
"""


def mark_type_only_imports(source: str) -> str:
    def rewrite(match: re.Match) -> str:
        names = []
        for raw in match.group(2).split(","):
            name = raw.strip()
            if not name:
                continue
            bare = name.removeprefix("type ").strip()
            if bare in TYPE_ONLY_EXPORTS and not name.startswith("type "):
                name = f"type {bare}"
            names.append(name)
        return match.group(1) + ",\n  ".join(names) + match.group(3)

    return re.sub(r"(import\s*\{)([^}]*)(\}\s*from)", rewrite, source, flags=re.S)


def record(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Run the reference implementation over ``cases`` and return its results."""
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "reference"
        shutil.copytree(REFERENCE, work)

        (work / "src" / "builder").mkdir(parents=True, exist_ok=True)
        (work / "src" / "builder" / "gbnf-rule.ts").write_text(BUILDER_STUB)
        for path in (work / "src").rglob("*.ts"):
            path.write_text(mark_type_only_imports(path.read_text()))
        (work / "hook.mjs").write_text(RESOLVE_HOOK)
        (work / "harness.ts").write_text(HARNESS)

        cases_path = work / "cases.json"
        cases_path.write_text(json.dumps(cases))

        result = subprocess.run(
            [
                "node",
                "--experimental-transform-types",
                "--no-warnings",
                "--import",
                "./hook.mjs",
                "harness.ts",
                str(cases_path),
            ],
            cwd=work,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            raise SystemExit(result.returncode)

        return json.loads(result.stdout)


def main() -> int:
    recorded = record(CASES)
    FIXTURES.mkdir(parents=True, exist_ok=True)
    (FIXTURES / "reference.json").write_text(json.dumps(recorded, indent=2) + "\n")
    print(f"recorded {len(recorded)} cases to {FIXTURES / 'reference.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
