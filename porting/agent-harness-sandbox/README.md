# agent-harness-sandbox

Runs a coding agent's CLI inside a locked-down container.

The caller supplies a prompt, an agent, an image and output directories.
Whatever the agent works on arrives in that image: `build_agent_image` takes a
Dockerfile modifier and named build contexts, so a caller copies its own tree in
at build time, while the network is still open. Nothing is mounted for the agent
to read, because a bind shadows the image's own filesystem at the mount point.
The container is removed when the run ends, so its writes go with it. Outputs
mount read-write and are the caller's own directories. The container
drops all capabilities, runs with `no-new-privileges`, and reaches the network
only through an egress proxy that allows the agent's own endpoints. The proxy
log and the session transcript land on the host.

Library only, no CLI. `build_agent_image` builds the images in `sandbox/` and
returns the agent's tag. `run_agent_harness_sandbox` runs the prompt in
whatever image it is handed. Every option is required; nothing has a default.

`ClaudeAgent` is wired up. `PiAgent` exists but is not.

Knows nothing about porting, gbnf, or what is in the image it is handed.
Depends on nothing else in this repo.
