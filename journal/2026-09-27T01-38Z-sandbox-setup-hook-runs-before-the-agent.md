# 2026-09-27T01:38Z sandbox setup hook runs before the agent

Issue #75, PR #81. `run_agent_harness_sandbox` takes a required `setup` argv,
or `None`. The container starts detached and holds open; setup runs in it by
`docker exec` with the lockdown's egress network attached and no proxy env,
then the network is detached and the agent runs by a second exec under the
proxy. Kevin, 2026-09-26: "agent-harness needs to expose a way to run an
arbitrary command, perhaps with docker exec or whatever makes sense." The
open egress question from the pipeline note is settled on the side of running
the install before the lockdown applies to it, so the agent's allowlist is
unchanged. Unit red run 34 failed, 1 passed; then 145 passed. Integration 24
passed. The e2e setup test fetched `registry.npmjs.org/-/ping` in setup and
the agent read back `200`; 2 passed, live run.
