# The Preparation Step

*How gbnf-experiment turns the gbnf repository into the tree a porting agent sees. Design of record as of 2026-09-17, with the current state and the issues that close the gap.*

The porting agent runs inside a container. Before it starts, something has to put a reference implementation and, under some conditions, a test suite in front of it. That something is the preparation step. This note says what it does, what it deliberately does not do, and where the code is on the way there.

## What it produces

One directory tree, `/workspace` inside the agent's container:

```
/workspace
├── reference_implementation/   the gbnf package in the source language, whitelisted
├── tests/                      generated test suites, one directory per language selected
│   ├── python/                 present only when the condition includes python tests
│   └── typescript/             present only when the condition includes typescript tests
└── ported_implementation/      empty, writable, the agent's output
```

`reference_implementation` and `tests` are writable. The agent may do what it likes to them; the run's only output is `ported_implementation`.

## The four moves

1. **Clone gbnf at a pinned commit.** [thekevinscott/gbnf](https://github.com/thekevinscott/gbnf) at the SHA in `gbnf_experiment.config`. The pin, not a branch, is what makes the corpus reproducible.

2. **Patch it.** Patches under `packages/gbnf-experiment/docker/gbnf-prepare/patches/` are applied with `git apply`. Today there is one: it adds a python template to the one shared test-spec file that had only a typescript one, so test-writer can emit a complete python suite. A second patch, removing `src/index.ts`'s re-exports of the withheld `src/builder/` directory, replaces the per-run regex that does that now (#33). Patches are the only edits to gbnf. They are small, reviewable as diffs, and applied once at build time.

3. **Run test-writer.** gbnf keeps one language-neutral test spec under `packages/gbnf/test/`, markdown files with a code-block template per language. gbnf's own `packages/test-writer` renders that spec into real test files. The preparation step runs it once per language. The output is a generated suite, the same one gbnf itself generates into a gitignored directory before running its integration tests. The python suite reads its grammar fixtures from disk, so those fixture files ride along with it.

4. **Select files by whitelist.** gbnf-experiment names, per package, which files the agent sees: `PYTHON_PATTERNS` and `TYPESCRIPT_PATTERNS` in `reference_patterns.py`, gitignore syntax, default deny, `!` negation. porting-harness's `select_files` applies a pattern list to a file listing and returns the selected paths. That is the only place gbnf's layout is named, and the only place a condition varies what the agent sees. Colocated tests (`*_test.py`, `*.test.ts`) are negated in every list; a condition's tests flag adds `/python/**` or `/typescript/**` over the generated suites and nothing else.

That is the whole step. Every file the agent sees is one of: a tracked gbnf file at the pin, possibly patched, that the whitelist admitted; or a test-writer output the whitelist admitted.

## Where each move runs

Two Docker stages, one Dockerfile owned by gbnf-experiment.

**Prepare stage.** Moves 1 to 3. Clone, patch, `pnpm install`, build and run test-writer. Writes a listing of every file it holds. Everything here is a cached layer keyed on the pin and the docker context, so it builds once.

**Host.** Reads the listing out of the prepare stage and runs `select_files` over it with the condition's pattern list. The result is an explicit list of paths. The same list goes into the run's manifest as `included`; the manifest is the only durable record of what the agent saw. No pattern evaluation happens inside any container.

**Final stage.** `FROM` the agent-harness-sandbox image. `ARG FILES` carries the explicit list, used only in the last layers: copy exactly those paths out of the prepare stage into `/workspace`, then install the reference's dependencies (`uv sync`, `pnpm install`) and the test runner for the target language. Docker caches per distinct `FILES` value, so switching conditions costs one small layer, not a rebuild. Dependencies are installed in the container they run in; nothing is copied in from the host.

**Run.** porting-harness starts the final image with one mount, `ported_implementation`, read-write. The proxy sidecar and the network lockdown are unchanged and are documented in [SANDBOX.md](SANDBOX.md).

## What it deliberately does not do

- **No `git archive`.** An earlier version extracted the package directories with `git archive` to keep `node_modules` and build output out. The whitelist does that job; the archive is redundant and, because it reads the commit rather than the working tree, it would silently drop a patch to a package file.
- **No host-side corpus cache.** An earlier version wrote the prepared tree to a keyed directory under the user's cache and reassembled from it per run. Docker's layer cache replaces it. A host process once compiled bytecode into that cache and the agent received it; there is no cache for that to happen to now.
- **No harness-authored instructions in the tree.** README files telling the agent how to run the suite are gone. Wiring the suite to the port is part of the task. One harness-authored file, a vitest config that aliased `gbnf` to the port, is still in place pending a decision.
- **No pattern evaluation in a container.** The container receives file paths, never patterns.
- **No read-only reference.** The reference is the agent's to edit. Only the output mount matters.
- **No pre-installed toolchain in the sandbox image.** The final stage installs what the reference and the target language need, from the reference's own lockfiles.
- **No edits to gbnf outside `patches/`.** Bugs in gbnf are experiment input.

## Current state

| Move | Today | Target | Issue |
|---|---|---|---|
| Clone, patch, test-writer at build time | yes, since #36 | same | done |
| Container named gbnf-prepare | yes, since #37 | same | done |
| Whitelist replaces the removers | on the whitelist branch | same | #26 |
| Tests selected by pattern, not copied by flag | copytree by flag | pattern | #34 |
| Selection on the host, `ARG FILES` into a final stage | host selects from a cache dir, then bind-mounts | multistage | #35 |
| `git archive`, host cache, READMEs, uid workarounds removed | present | removed | #35 |
| Builder re-exports removed by patch | per-run regex | patch | #33 |
| Reference writable | read-only bind mount | writable, in the image | #35 |

Order: #26, then #34, then #35, then #33.
