# port_codebase

Ports a reference library into another language, inside a [botbox](https://github.com/thekevinscott/botbox).

`port_codebase` takes a prompt, a source directory and an output directory. The agent reads the source and writes the port to the output.

The harness's system prompt, `prompts/prompt.txt`, tells the agent where those two directories are. The caller's prompt is appended to it and describes the source's layout: what is the library, what is a suite, what to port to. Paths in it are relative to the source.

Does not produce tests and does not grade the result.

The image ships Python 3.14.3, uv 0.12.10, pytest 9.1.1, vitest 2.1.3 and pnpm 9.4.0.

## Usage

```python
from botbox import ClaudeAgent
from port_codebase import port_codebase

result = port_codebase(
    agent=ClaudeAgent(model="claude-opus-5", effort="high"),
    prompt="`Port it to python. `tests/` is the suite for the port.",
    source=Path("./reference"),
    output=Path("./port"),
)

print(result.stdout)      # claude's JSON result
print(result.transcript)  # botbox RunResult: session jsonl by path
print(result.proxy)       # the proxy log
```

```python
port_codebase(
    *,
    agent: Agent,
    prompt: str,
    source: Path,
    output: Path,
) -> RunResult
```

Returns [botbox's `RunResult`](github.io) unchanged. 

