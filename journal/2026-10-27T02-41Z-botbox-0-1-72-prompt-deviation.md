# 2026-10-27T02:41Z botbox 0.1.72 changes the prompt again; accepted

The move to botbox 0.1.72 (PR #241) changes the Claude agent Dockerfile: a new step creates `/home/user/.claude/projects` with mode 777, and the setuid-stripping step also makes `/etc/passwd` writable, so the agent can run as the host uid. port_codebase pastes that Dockerfile into the prompt, so v2-models-effort runs launched after this see a different prompt and image than runs on botbox 0.1.1.

Kevin: "I think Dockerfile changes in the prompt are ok". Recorded in `experiments/v2-models-effort/files/DEVIATIONS.md`.
