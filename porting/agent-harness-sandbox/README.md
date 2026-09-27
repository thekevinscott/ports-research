# agent-harness-sandbox

Runs a coding agent's CLI inside a locked-down container.

The caller supplies a prompt, an agent, an image, one `input` folder, output
directories, and a setup command or `None`. The `input` folder is copied and the
copy mounts writable at `/input`, then is thrown away when the run ends: the
agent can install and scratch there, and nothing it writes reaches the caller's
folder. Outputs mount read-write and are the caller's own directories. The
container drops all capabilities, runs with `no-new-privileges`, and reaches the
network only through an egress proxy that allows the agent's own endpoints. The
proxy log and the session transcript land on the host.

The setup command runs in the container before the agent, against that copy,
with the network open and no proxy env, so a dependency install reaches its
registry directly. The network is taken back before the agent starts; the
agent's reach is the allowlist and nothing more.

Library only, no CLI. `build_agent_image` builds the images in `sandbox/` and
returns the agent's tag. `run_agent_harness_sandbox` runs the prompt in
whatever image it is handed. Every option is required; nothing has a default.

`ClaudeAgent` is wired up. `PiAgent` exists but is not.

Knows nothing about porting, gbnf, or what is in the mounted directories.
Depends on nothing else in this repo.
