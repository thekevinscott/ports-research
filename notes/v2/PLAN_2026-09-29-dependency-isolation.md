# Dependency isolation

Written 2026-09-29. Supersedes the dependency-isolation portions of
`notes/PLAN_2026-09-16-v2.md`. Everything here was decided by Kevin in the
2026-09-29 session; items he left open are marked open rather than filled in.

## The problem

The agent must be able to install the dependencies a port needs, and must never
be able to reach gbnf's own implementation in the target language.

Deny-by-name at a registry does not work. Three facts establish it:

- `gbnf` is published on both npm and PyPI. The PyPI package at version 0.0.32
  declares `pytest-watcher>=0.4.3` — the same dependency the repository's own
  Python package declares. It is the Python implementation, published.
- `json2gbnf` is a sibling package in the same `ambient-labs/GBNF` monorepo,
  published on both registries, and carries roughly 27,000 characters of gbnf's
  built implementation in its sourcemap `sourcesContent`. It declares no
  dependencies, so nothing about its manifest marks it as related.
- `sql2gbnf` is published on npm from the same monorepo and has the same shape.

So the leak is bidirectional: porting TypeScript to Python, `pip install gbnf`
is the answer key; porting Python to TypeScript, `npm i gbnf` is. A name rule
would have to cover republication under unrelated names, which is unbounded.

Detection after the fact is not an acceptable substitute. The point of the
experiment is to study the nature of porting, which requires that target
material be kept from the agent; observing that it cheated makes the run a
waste, exactly as it did in v1.

The conclusion: installs move to build time, and the running agent gets no
registry egress.

## Why gbnf is a good test case for this

The library has no runtime dependencies in either language. The JavaScript
`package.json` has no `dependencies` key at all, only build and lint
devDependencies. The Python `pyproject.toml` declares one, `pytest-watcher`.
A port needs a test runner and nothing else. This is worth stating in the
write-up as additional justification for the choice of library.

## Shape

A multi-stage Docker build. Stage 1 has network and installs. Stage 2 has no
registry egress and inherits what stage 1 produced.

The sandbox stays generic. It learns no language, no filenames, and no paths.

### 1. `modify_dockerfile`

`agent-harness-sandbox` gains a `modify_dockerfile: Callable[[str], str] | None`
parameter. Text in, text out: the caller rewrites the Dockerfile, and `None`
leaves it untouched. This is what keeps lockfile names and install commands out
of the sandbox.

Generation must be deterministic — Docker keys a layer on the instruction text,
so an unsorted dependency list would miss the cache on reordering.

### 2. The input mount is removed

`/input` is currently a scratch copy of the caller's folder, bind-mounted at run
time. A bind mount shadows whatever the image holds at that path, so anything
installed into `source/` during the build would be invisible at run time.

Instead the caller's Dockerfile modification copies `source/` in during stage 1.
The agent's writes to `source/` are still discarded, because the container is
ephemeral — the same property the scratch copy provided.

### 3. The target mount stays

`target/` is how the port reaches the host, so it keeps its bind mount. That
means dependencies cannot be baked into the image at that path; see section 6.

### 4. Stage 1

Driven entirely by the caller's Dockerfile text:

- Copy `source/` in and install its dependencies in place, from the manifest it
  already ships — `pnpm install` for a TypeScript source, `uv sync` for a Python
  one.
- Copy the *target* lockfile to `/tmp`, never into `target/`. Read it, generate
  a pinned install list, and install to an unmounted staging path.
- The target dependency list is every non-local entry in the lockfiles, plus
  `ruff==0.16.9`. Local entries are identifiable mechanically:
  `source = { editable = "." }` in `uv.lock`, and `link:`/`workspace:` in
  `pnpm-lock.yaml`. That excludes `gbnf` and `test-writer` without maintaining a
  name list.
- No hash pinning. Hashes are all-or-nothing in uv and `ruff` has no lockfile
  entry to take a hash from, and the byte guarantee adds nothing when stage 1
  fetches from the registry at build time regardless.
- Stage 1 runs as the normal user, not root. Root-owned files in `target/` would
  not be writable by `USER node`.

The target lockfile never lands where the agent can read it, because gbnf's
lockfiles leak the answer. `uv.lock` carries `name = "gbnf"` and
`version = "0.0.32"`. The monorepo `pnpm-lock.yaml` is 8,877 lines and its
`importers` section names `packages/gbnf/javascript`,
`packages/json2gbnf/javascript`, `packages/sql2gbnf/javascript` and
`packages/test-writer` — the sibling map, including the two published packages
that carry gbnf's source.

Note that `pyproject.toml`, which the agent must see, carries
`Homepage = "https://github.com/ambient-labs/GBNF/packages/gbnf"`. That is a
source-side leak independent of lockfiles and is not addressed here.

### 5. Stage 2 has no registry egress

Already true on `main`. The sandbox proxy config sets `FilterDefaultDeny Yes`
with an allowlist filter, so registries are unreachable unless something adds
them. Nothing does.

### 6. The dependencies are copied into `target/` at container start

Because `target/` is a bind mount, the copy has to happen after the mount
exists. `gbnf-experiment` does it in the run command, ahead of the agent CLI.

- `cp -a`, to preserve pnpm's relative symlinks into `node_modules/.pnpm`. A
  dereferencing copy breaks them and multiplies the size.
- Python dependencies land in `target/.deps`, a flat
  `uv pip install --target` directory, with `PYTHONPATH` pointing at it. Not a
  venv: a venv records the base interpreter's container path in `pyvenv.cfg` and
  absolute shebangs in `bin/`, so it cannot be read from the host afterwards,
  which is the whole reason for putting dependencies in `target/`.
- TypeScript dependencies land in `target/node_modules`.
- A subdirectory rather than flat into `target/` so the analyses that measure
  the port's own source are not confounded by pytest and ruff sitting beside it.

`mv` would not be faster. The staging path is in the image's overlay filesystem
and `target/` is a bind mount, so a move is cross-filesystem and degrades to
copy-then-unlink. The cost is acceptable regardless: the whole monorepo
`node_modules` is 323 MB across 38,823 files and a vitest-and-typescript tree is
a fraction of that, so the copy is seconds against a run measured in minutes.

### 7. The prompt names the package manager for each target

## Deliberately not doing

- No registry mirror or curated index. It is the right tool if a port ever needs
  a library that was not predicted, and that has no instance in v2.
- No `pnpx`/`uvx`. They resolve from the registry at call time.
- No hash pinning, for the reason in section 4.
- No post-hoc contamination detection.
- No `docker cp` copy-out. The `target/` mount stays.

Tarballs in the run image are acceptable. The property that matters is that no
gbnf artifact was ever fetched, not that the image is free of fetched bytes.

## Known gaps

**Provider-side server tools do not traverse the proxy.** If `web_search` or
`web_fetch` are enabled, the agent can read the GBNF repository on GitHub
without the sandbox proxy ever seeing the request. This is wider than the
registry hole and is unresolved. Whatever the model memorized in training is
not addressable at all.

**`stage_auth`'s credential is unidentified** — API key or subscription. It
determines whether an organization-level server-tool switch governs web search
and fetch.

## Open

- The target dependency list beyond `pytest`, `pytest-describe`,
  `ruff==0.16.9` / `vitest`, `typescript`, `eslint`, `prettier`, once the
  non-local filter is applied to the real lockfiles.
- Whether `analysis/execute-test-suite` switches to the dependencies now present
  in `target/`. It currently brings its own toolchain via `pnpm dlx` with
  network, and gets away with it only because gbnf has no runtime dependencies.
  A port that imports a real library would break that.

## Resolved in passing

- `test-writer` is `"private": true` and returns 404 on both npm and PyPI. It is
  a workspace-only dependency and cannot be fetched, so the risk flagged for it
  in earlier sessions is closed.
- `sql2gbnf` is published on npm from the same monorepo and had not previously
  been named as a vector.
