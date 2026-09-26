# ports

An experiment on LLM-driven porting of a codebase between languages.

The subject is [gbnf](https://github.com/thekevinscott/gbnf), which has
hand-written TypeScript and Python implementations sharing one test suite. An
agent in a sandbox gets one implementation as the reference, with or without
each language's test suite mounted, and is asked to port it to the other
language. Scoring is a separate step: `execute-test-suite` runs the full
derived suite against the port, so the suite is held out only for runs that
did not mount it.

## Core packages

Three packages, each configuring the one above it.

- `packages/agent-harness-sandbox` — a sandboxed agent. Its `-v` mounts are
  configurable, its network access is restricted, and it is hardened reasonably
  well. Library only, no CLI: `build_agent_image` builds the images in
  `sandbox/` and returns the agent's tag; `run_agent_harness_sandbox` runs the
  agent's CLI (`ClaudeAgent`, `claude -p`; `PiAgent` exists but is not wired
  up) in whatever image it is handed, inside a container behind an egress
  proxy.
- `packages/porting-harness` — configures agent-harness-sandbox, provides a
  prompt (`src/porting_harness/prompt.txt`) and a layout. Reference, tests and
  output are synced locally: direct bind mounts, not copies. Library only:
  `run_porting_harness` expects `source/` and `tests/` under the reference
  directory, mounts each read-only, and binds the output directory writable.
- `packages/gbnf-experiment` — configures porting-harness specifically for
  gbnf. Runs necessary pre-work such as generating the test suite (the
  gbnf-prepare image in `docker/gbnf-prepare`, cached under
  `~/.cache/ports/gbnf-experiment/prepared/`). Otherwise minimal. CLI
  `run-gbnf-experiment`; each invocation writes one run directory under `data/`.

## Reference provenance

The gbnf-prepare Dockerfile clones `github.com/thekevinscott/gbnf`, checks out
the pin in `gbnf_experiment/config.py` (`13f1aca`, the merge of gbnf PR #81)
and applies `patches/`.

Runs banked before the bundle removal record `derivation_cache_key =
390bf534c55d496b` in their manifests; the key after that was
`af673dbe41be73ce`. Only the hash input set changed, not the corpus:
rebuilding at the new key and running `diff -rq` against the old tree reports
both identical across all 250 files, differing only in `__pycache__` bytecode
the old tree accumulated after derivation. Manifests are left as banked.

Renaming the container to gbnf-prepare moved the key again, to
`771a734d60ecbae5`. Only names changed; the corpus the container emits is the
same.

## Supporting packages

- `packages/execute-test-suite` — CLI `execute-test-suite --language
  <python|typescript|javascript> --target <dir>`. Runs gbnf's derived test
  suite against one ported implementation on the host, prints one line of JSON
  with pass, fail, error and skip counts, and exits 0 on success. Needs the
  prepared corpus cache, which a gbnf-experiment run builds. Calls no model.
- `packages/generate-embedding` — CLI `generate-embedding <file> --model
  <name>`. Embeds one code file through an OpenAI-compatible `/v1/embeddings`
  endpoint (`GENERATE_EMBEDDING_BASE_URL`, optional `GENERATE_EMBEDDING_API_KEY`)
  and prints the vector as JSON, or writes a float32 `.npy` with `--output`.

## Proposed projects

`proposed-projects/` holds analysis tools built alongside the experiment and
not yet promoted to `packages/`. CLI lines are abbreviated; `--help` has the
full usage.

- `contamination-probe` — CLI `perturb-reference-tree`. Renames the library
  and every public symbol in a reference tree, reshuffles its layout, and
  writes the perturbed copy plus a `rename-manifest.json`. It runs no port.
- `measure-complexity-curve` — CLI `measure-complexity-curve --language
  <python|typescript> --target <dir>`. Times a gbnf implementation against
  generated grammars of increasing size and prints a JSON report of the
  time-complexity shape.
- `round-trip-experiment` — CLI `reverse-port stage|record|run --run <forward
  run dir>`. Stages a banked port as a derivation of its own and runs it back
  through `run-gbnf-experiment` into the language it came from, both suites
  included; legs land under the package's `reverse/<forward run id>/`.

## Runs

Each run lands in `packages/gbnf-experiment/data/<timestamp>_<id>/` with
`manifest.json`, `ported_implementation/`, `transcript/`, `proxy.log`, and
`result.json` once the run finishes. The manifest records the condition
(source language, test flags, effort, model), the gbnf commit, the sandbox
image id and the harness commit. `result.json` is the agent CLI's JSON output
(usage tokens, turns), not a score. Start a run from `packages/gbnf-experiment`:

```
uv run run-gbnf-experiment --source-language python --include-python-tests --include-typescript-tests
```

Optional flags: `--model` (default `claude-opus-5`), `--effort` (default
`high`), `--agent` (only `claude` is wired up), `--debug`.

## Setup

Docker, uv, pnpm, Node, hyperfine and just. Node runs the
`pnpm dlx` calls in the typescript paths of execute-test-suite and
measure-complexity-curve; hyperfine is measure-complexity-curve's timer.
Python 3.14 or later. No root workspace: `uv sync` in each
package. The core packages chain through editable path deps: porting-harness
-> agent-harness-sandbox, gbnf-experiment -> porting-harness,
execute-test-suite -> gbnf-experiment. gbnf-experiment reads
`GBNF_EXPERIMENT_*` env vars (pydantic-settings; among them `DATA_DIRECTORY`,
`PREPARED_DIRECTORY`, `GBNF_COMMIT`, `IMAGE_TAG`) and `XDG_CACHE_HOME` for
the cache root.

Auth: no API key env var. `ClaudeAgent` copies the host's
`~/.claude/.credentials.json` into the sandbox, so the host needs a logged-in
Claude Code. The sandbox's egress allowlist is `api.anthropic.com` only.

## Notes

`notes/SANDBOX.md` is an account of the container isolation the porting agent
runs under: what the sandbox mounts, what it withholds, and what it does not
cover.

`papers/` at the repo root is a 741MB arXiv corpus, gitignored and rebuildable
with `scripts/harvest`. The literature survey that reads it is not published
with the repo.

Session handoffs, audits and dated analysis batches are kept on disk under
`internal/`, outside the published repo.

## Conventions

Root `AGENTS.md` covers the test tiers (`just test-unit`, `test-integration`,
`test-e2e`; one justfile per package) and the rule that the gbnf source is
never edited. Never run a bare `uv run pytest`: it collects `tests/e2e`, which
starts real containers and in porting-harness makes billed LLM calls.

## License

MIT. See `LICENSE`.
