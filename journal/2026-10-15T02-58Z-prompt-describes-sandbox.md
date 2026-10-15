# 2026-10-15T02:58Z — Experiment prompt now describes the sandbox

Kevin paused the Fable study to review the prompt: "I'm not sure the prompt is ready as it is." He had found an agent struggling with uv in one transcript.

Counts over the 267 V2 transcripts (error text in tool results; 137 javascript-source, 130 python-source): uv "network was disabled" 50 js / 22 py; uv "No solution found" 44 js / 4 py; ModuleNotFoundError pytest_describe 42 js / 8 py; "Cannot find package 'vitest'" 44 py; uv venv into read-only /input 29 py.

Facts verified inside the built image by two Opus subagents (results at /tmp/claude/sandbox-facts/): registries blocked, only the model API reachable; /input read-only; pytest + pytest-describe and vitest on PATH; uv sync fails, uv run fails wherever a pyproject exists; pnpm and npm install fail; an ESM vitest config cannot import vitest/config, a .cjs one can.

Prompt line 2 replaced with three lines stating those facts (branch `sandbox-prompt`). Kevin: "defensible as the first experiment was about how tests affect ports. This is about how models produce different ports." The 192 V2 runs and the six Fable runs banked before the pause used the old prompt. Dockerfile-in-the-prompt rejected: the facts that bite are runtime mounts and network, not image layers.
