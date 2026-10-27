# port_codebase

Ports a reference library into another language, inside a [botbox](https://github.com/thekevinscott/botbox).

`port_codebase` takes a prompt, a source directory, a port directory and an artifact directory. The agent reads the source and writes the port to the output. Botbox writes its logs and transcripts to `artifacts`.

The harness's system prompt, `prompts/prompt.txt`, tells the agent where those two directories are, that there is no network, and shows it the two Dockerfiles the image was built from (botbox's agent image, then this package's `Dockerfile`), read from disk at each call. The caller's prompt is appended to it and describes the source's layout: what is the library, what is a suite, what to port to. Paths in it are relative to the source.

Does not produce tests and does not grade the result.

The image ships Python 3.14.3, uv 0.12.10, pytest 9.1.1 with pytest-describe 3.2.0, vitest 2.1.3 and pnpm 9.4.0.

## Usage

```python
from botbox import ClaudeAgent
from port_codebase import port_codebase

result = await port_codebase(
    agent=ClaudeAgent(model="claude-opus-5", effort="high"),
    prompt="`Port it to python. `tests/` is the suite for the port.",
    source=Path("./reference"),
    output=Path("./port"),
    artifacts=Path("./run-artifacts"),
)

print(result.exit_code)
print(Path("./run-artifacts/stdout.txt").read_text())
print(Path("./run-artifacts/proxy.log").read_text())
```

```python
async def port_codebase(
    *,
    agent: Agent,
    prompt: str,
    source: Path,
    output: Path,
    artifacts: Path,
) -> RunResult
```

Returns botbox's `RunResult` unchanged. Its only field is `exit_code`.
