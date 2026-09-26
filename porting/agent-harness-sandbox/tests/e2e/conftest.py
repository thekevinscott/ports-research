from dataclasses import dataclass
from pathlib import Path

import pytest

from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent
from agent_harness_sandbox.build_agent_image import build_agent_image
from agent_harness_sandbox.run_agent_harness_sandbox import run_agent_harness_sandbox

MODEL = "claude-opus-5"
EFFORT = "low"
HOME = "/workspace"
PROBE_TARGET = f"{HOME}/probe"
OUTPUT_TARGET = f"{HOME}/out"
SCRIPT = "probe.sh"
REPORT = "report.txt"
DENIAL = "Proxying refused"

PROMPT = (
    "Run `sh {script}` and write its complete output, byte for byte, to {report}. "
    "Add nothing, drop nothing, interpret nothing, and create no other file."
)

LINE = 'printf "%s\\t" "{name}"; ({command}) 2>&1 | tr "\\n" " "; echo'


@dataclass(frozen=True)
class Session:
    """One finished sandbox run and the three places its evidence landed."""

    output: str
    report: dict[str, str]
    transcripts: Path
    proxy_log: Path

    @property
    def denials(self) -> list[str]:
        return [line for line in self.proxy_log.read_text().splitlines() if DENIAL in line]


@pytest.fixture(scope="session")
def sandbox(tmp_path_factory):
    """Run one probe script through the sandbox and collect what came back out.

    The script is mounted as an input and its output read back from a bound output
    directory, so the whole exchange goes through the package's own entry point.
    """

    def run(probes: dict[str, str]) -> Session:
        root = tmp_path_factory.mktemp("sandbox")
        probe, outputs, transcripts = root / "probe", root / "out", root / "transcripts"
        for directory in (probe, outputs, transcripts):
            directory.mkdir()
        (probe / SCRIPT).write_text(
            "".join(
                LINE.format(name=name, command=command) + "\n" for name, command in probes.items()
            )
        )
        proxy_log = root / "proxy.log"
        agent = ClaudeAgent()
        output = run_agent_harness_sandbox(
            PROMPT.format(script=f"{PROBE_TARGET}/{SCRIPT}", report=f"{OUTPUT_TARGET}/{REPORT}"),
            agent=agent,
            image=build_agent_image(agent=agent, debug=False),
            inputs={probe: PROBE_TARGET},
            outputs={outputs: OUTPUT_TARGET},
            envs={},
            debug=False,
            home=HOME,
            transcripts=transcripts,
            proxy_log=proxy_log,
            effort=EFFORT,
            model=MODEL,
        )
        fields = (
            line.split("\t", 1)
            for line in (outputs / REPORT).read_text().splitlines()
            if "\t" in line
        )
        return Session(
            output=output,
            report={name: value.strip() for name, value in fields},
            transcripts=transcripts,
            proxy_log=proxy_log,
        )

    return run


@pytest.fixture
def options(tmp_path):
    """Every argument one run needs, with the caller's overrides on top."""

    def build(**overrides):
        agent = ClaudeAgent()
        return {
            "agent": agent,
            "image": build_agent_image(agent=agent, debug=False),
            "inputs": {},
            "outputs": {},
            "envs": {},
            "debug": False,
            "home": HOME,
            "transcripts": tmp_path,
            "proxy_log": tmp_path / "proxy.log",
            "effort": EFFORT,
            "model": MODEL,
            **overrides,
        }

    return build
