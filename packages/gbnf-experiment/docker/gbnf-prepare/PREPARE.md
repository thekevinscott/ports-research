# The Preparation Step

*How gbnf-experiment turns the gbnf repository into a prepared tree.*

The porting agent runs inside a container. Before anything can be put in front of it, gbnf has to be fetched, adjusted, and built. That is the preparation step. It ends with a prepared tree and a listing of every file in it. Which of those files the agent sees is the whitelist's business, decided per condition, and is not part of this note.

## The three moves

1. **Clone gbnf at a pinned commit.** [thekevinscott/gbnf](https://github.com/thekevinscott/gbnf) at the SHA in `gbnf_experiment.config`. The pin, not a branch, is what makes the corpus reproducible.

2. **Patch it.** The patches under `patches/` are applied with `git apply`, in order. They are the only edits made to gbnf. What each one does, and the rule for adding one, is in [patches/PATCHES.md](patches/PATCHES.md).

3. **Build.** `pnpm install`, then gbnf's own build for its test suites. gbnf keeps one language-neutral test spec under `packages/gbnf/test/`, markdown files with a code-block template per language, and `packages/test-writer` renders that spec into real test files. That runs once per language. The output is the same generated suite gbnf itself builds into a gitignored directory before running its integration tests.

That is the whole step. Every file in the prepared tree is one of: a tracked gbnf file at the pin, possibly patched; or a build output.

## Where it runs

One Docker stage, `gbnf-prepare`, built from the Dockerfile in this directory. The three moves are `RUN` layers keyed on the pin and the docker context, so the stage builds once and is cached until either changes. Its last layer writes a listing of every file it holds.

The stage is not the agent's container. It is the source that a later stage copies from, by explicit file path, into the image the agent runs in.
