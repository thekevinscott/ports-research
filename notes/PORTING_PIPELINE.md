# The porting pipeline, step by step

What each package in the chain does and why. Settled with Kevin on
2026-09-26. Whys in quotes are his words. Whys without quotes were proposed
by the agent and accepted in the same conversation.

The chain is gbnf-experiment, then porting-harness, then
agent-harness-sandbox. Each package knows only about the one below it.

## gbnf-experiment

Everything gbnf-specific. The prepare image is built once per condition.
Build args name the source language and which generated test suites to
copy into `/reference`. Steps 1 through 6 happen inside that image, at
build time.

1. **Clone gbnf at the pinned commit.**
   "we clone and pin so that we have reproducibility"
2. **Apply patches.**
   "we apply patches because we don't want to modify the source repo"
   This also corresponds to removing code we don't want to expose to the
   porting agent.
3. **Install node modules and build test-writer.**
4. **Run test-writer for both languages, then copy the flagged suites.**
   Kevin, 2026-09-27: "Tests write regardless of flags and should write to
   /tmp/tests/{lang}." "It's later in the script that we copy them based
   on the flags." So test-writer writes `/tmp/tests/<lang>` for every
   language, before the condition build args are declared, and each flag
   copies its suite to `/reference/tests/<lang>`. gbnf's tests are written
   once, in a language-neutral form; test-writer emits a runnable suite per
   language. Two suites can be present at once, so tests keep the
   per-language subfolder.
   Corrected 2026-09-27. The first version of this step said "per flag"
   and wrote to `/reference/tests/<lang>` directly; Kevin: "NOPE not what
   I asked for."
5. **Copy the source language into `/reference/source`.**
   The whitelist is applied here, inside the container, during the copy.
   Plain shell, no host involvement. "I think that that means the
   whitelist glob step can happen in the docker container, right?" What
   is left out, and why, is recorded next to the filter. Whether it is
   written as a whitelist or a blacklist "doesn't really matter."
6. **Clean up build litter.** (Optional.) Remove files generated in the
   course of the above, such as `__pycache__`. Maybe unnecessary.

`/reference` is the folder that comes back to the host, whole. It is the
reference exactly as the agent will see it. Nothing on the host selects,
stages or caches. gbnf-experiment hands the folder to porting-harness and,
when the run returns, writes the run directory under `data/runs`:
manifest, result, transcript, proxy log.

### Tests

The container's output is what the agent sees, so it is what gets tested.
For each of the eight conditions (two source languages, each test suite
on or off), build the image and assert that `/reference` holds exactly
the expected files. "We _will_ want tests on the gbnf-experiment
container, specifically that the reference folder produced for the 8
conditions is what we expect."

## porting-harness

Generic. Knows nothing about gbnf or conditions.

7. **Receive a folder containing the reference.**
   Might be source files alone, might be `source/` and `tests/` (gbnf
   will be this).
8. **Receive a prompt.**
   This (likely) includes information about the code setup on disk.
9. **Run a post-copy step in agent-harness-sandbox.**
   This might be an `npm install` or `uv sync` or both. Installing inside
   the container, rather than copying `node_modules` from the host, is
   what answers "Copying over node_modules risks a whole lot of bullshit
   like if the host system mismatches the docker container system."
10. **Ask agent-harness-sandbox to run the agent** with the prompt, the
    reference mounted read-only, outputs mounted writable.
11. **Return the port and the transcript** to the caller.

## Open

**Egress for the post-copy install.** `npm install` and `uv sync` need
the network. Either step 9 runs before the proxy lockdown, or the proxy
allows the registries. A sandbox decision, not yet made.

## Superseded

Kevin, 2026-09-17: "The Docker container should receive an array of every
single individual file. Who is evaluating patterns? There should be no
evaluation within the Docker container." Replaced by step 5 on
2026-09-26: the filter runs in the container, at build time, as plain
shell. With it go the host-side listing, the build-ARG whitelist, the
host cache and its key, the staging step, and the plan to bake the
selected reference into a second image.
