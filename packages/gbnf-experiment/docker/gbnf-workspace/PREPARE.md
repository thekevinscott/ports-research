# The Workspace Image

This is how `gbnf` (the repo under test) gets prepared and fed to an agent. One multistage Dockerfile, three stages.

## 1. Clone

`gbnf` gets cloned at a pinned commit. The commit is old enough to be pre-agentic-development. 

We use [thekevinscott/gbnf](https://github.com/thekevinscott/gbnf) at the SHA in `gbnf_experiment.config`.

## 2. Patch

Out of the box, `gbnf` is missing some patches. For example, we need to apply some Python code to generate the Python version of the integration test suite.

Rather than push changes to the repo (which would make it harder to disambiguate agentic from non-agentic commits) we apply patches after clone.

What each one does, and the rule for adding one, is in [patches/PATCHES.md](patches/PATCHES.md).

## 3. Build

We run `pnpm install` and then we generate the integration tests on the fly. Integration tests are defined generically under `packages/gbnf/test/`.

The `prepare` stage ends by copying the two language trees to `/prepared/reference_implementation/<language>` and the generated suites to `/prepared/tests/<language>`, then writing every file path under `/prepared` to `/prepared.list`.

## 4. Select

On the host. `gbnf-experiment` reads `/prepared.list` out of the prepare stage and runs `porting_harness.select_files` over it with the condition's pattern list (`reference_patterns.py`). Nothing inside the container evaluates a pattern.

## 5. Bake

The `selected` stage takes `ARG FILES`, one path per line, and copies exactly those out of `/prepared`. The final stage is `FROM ${AGENT_IMAGE}` (agent-harness-sandbox's agent image) and copies the selection to `/workspace`, root-owned, so the agent reads it and cannot write it. The tag is a digest of the list, so each distinct selection is its own cached layer and the manifest records the image by id.
