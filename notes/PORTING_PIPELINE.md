# The porting pipeline, step by step

What each package in the chain does and why. Settled with Kevin on
2026-09-26. Whys in quotes are his words. Whys without quotes were proposed
by the agent and accepted in the same conversation.

The chain is gbnf-experiment, then porting-harness, then
agent-harness-sandbox. Each package knows only about the one below it.

## gbnf-experiment

Everything gbnf-specific. Steps 1 through 5 happen inside the prepare
image, at build time. Step 6 happens per run.

1. **Clone gbnf at the pinned commit.**
   "we clone and pin so that we have reproducibility"
2. **Apply patches.**
   "we apply patches because we don't want to modify the source repo"
3. **Install node modules and build test-writer.**
   No why needed. "it's self explanatory"
4. **Run test-writer once per language.**
   gbnf's tests are written once, in a language-neutral form. test-writer
   emits a runnable suite per language.
5. **Clean the tree.**
   Remove what the agent must never see. Lay out what remains as
   `source/<lang>` and `tests/<lang>`. "the gbnf-experiment preparatory
   image should be responsible for cleaning up the repo, and whatever is
   left is what gets copied over." Whether the cleanup is written as a
   whitelist or a blacklist is an implementation detail: "whether that's a
   whitelist or a blacklist for gbnf-experiment doesn't really matter."
   What gets removed, and why, is recorded next to the removal.
6. **Resolve the condition to directories.**
   A condition is a source language and which test suites to include. It
   maps to `source/<lang>` plus zero or more `tests/<lang>`. The condition
   is the only thing that changes between runs, so it is the only thing
   decided per run. This step is gbnf-experiment's alone: "this is specific
   to gbnf-experiment, not the other two."

gbnf-experiment hands those directories to porting-harness. When
porting-harness returns, gbnf-experiment writes the run directory under
`data/runs`: manifest, result, transcript, proxy log. `data/runs` is the
seam between porting and analysis.

## porting-harness

Generic. Knows nothing about gbnf or conditions.

7. **Receive a reference and, optionally, tests.**
8. **Put the reference in front of the agent as part of an image, not a
   bind mount.**
   "Copying over node_modules risks a whole lot of bullshit like if the
   host system mismatches the docker container system."
9. **Ask agent-harness-sandbox to run the agent** in that image with the
   porting prompt, outputs mounted.
10. **Return the port and the transcript** to the caller.

## agent-harness-sandbox

Knows nothing about porting.

11. **Run one agent in one container.** Inputs read-only, outputs
    writable, all capabilities dropped, egress only through the proxy.

## Open

**Who builds the image in step 8.** Either porting-harness, because it
owns the handoff from reference to agent, or gbnf-experiment, because it
already has a Dockerfile and would then hand porting-harness an image
instead of directories. Kevin's call. Until it is made, porting-harness
takes directories.

**Whether step 5 supersedes the 2026-09-17 position.** Kevin, 2026-09-17:
"The Docker container should receive an array of every single individual
file. Who is evaluating patterns? There should be no evaluation within the
Docker container." Step 5 puts the cleanup inside the prepare image, at
build time, as plain shell. The agent's reading is that the earlier
concern was pattern-evaluation machinery inside the container, and there
is none. Not yet confirmed by Kevin. If confirmed, the host-side listing,
the build-ARG whitelist and the host-side selection go away.
