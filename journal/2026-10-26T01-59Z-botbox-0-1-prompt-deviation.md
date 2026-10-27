# 2026-10-26T01:59Z botbox 0.1 changes the prompt; accepted

The move to botbox 0.1.1 (PR #236) changes the Claude agent Dockerfile: it installs `socat` and copies in `botbox-relay`. port_codebase pastes that Dockerfile into the prompt, so v2-models-effort runs launched after this see a prompt two lines longer than banked runs, in a different image. ports' own code since the last banked runs changed only to async.

Kevin chose to accept the change instead of pinning botbox 0.0.20. Recorded in `experiments/v2-models-effort/files/DEVIATIONS.md`.
