import json
from pathlib import Path

RULES = ("default_export",)

SHIM_TEMPLATE = """import {{ writeFileSync }} from "node:fs";
import * as port from {entry};
export * from {entry};

const exports = port as Record<string, unknown>;
const fired: string[] = [];
let entry = exports.default;
if (entry === undefined && "GBNF" in exports) {{
  entry = exports.GBNF;
  fired.push("default_export");
}}
writeFileSync({report}, JSON.stringify({{ rules_fired: fired }}));
export default entry;
"""


def adapt_typescript(directory: Path, *, port_entry: Path, report_path: Path) -> Path:
    """Write a `gbnf` entry shim over port_entry and return its path.

    The rule list above is the whole typescript policy. `default_export`: the
    reference suite does `import GBNF from 'gbnf'`; a port exporting only a named
    `GBNF` gets it as the default too. Everything else passes through untouched.
    """
    directory.mkdir(parents=True, exist_ok=True)
    shim = directory / "index.ts"
    shim.write_text(
        SHIM_TEMPLATE.format(
            entry=json.dumps(str(port_entry)), report=json.dumps(str(report_path))
        )
    )
    return shim
