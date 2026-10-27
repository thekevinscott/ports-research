"""CALLS CLAUDE FOR REAL AND IS BILLED. One `claude -p` session against Kevin's credentials.

Never re-run a failing test to chase green. A red one is a finding to report.
"""

import json

from botbox import ClaudeAgent

from port_codebase import port_codebase

MODEL = "claude-opus-5"
PNPM = "9.4.0"


def describe_the_box():
    async def it_ships_pnpm(tmp_path):
        source = tmp_path / "source"
        source.mkdir()

        result = await port_codebase(
            agent=ClaudeAgent(model=MODEL, effort="high"),
            prompt="Print the output of `pnpm --version` and nothing else.",
            source=source,
            output=tmp_path / "output",
            artifacts=tmp_path / "artifacts",
        )

        stdout = (tmp_path / "artifacts" / "stdout.txt").read_text()
        print(f"\n[live] stdout: {stdout[:2000]}")
        assert result.exit_code == 0
        assert PNPM in json.loads(stdout)["result"]
