# 2026-09-26T23:30Z prepare-image design replaced; gbnf-experiment to be rebuilt in one PR

Kevin walked the gbnf-experiment pipeline step by step and replaced the
whitelist-in-a-build-ARG design. The prepare image is now built once per
condition, with the source language and the two test flags as build args. Inside
it: clone at the pin ("so that we have reproducibility"), apply patches ("because
we don't want to modify the source repo", and patches also remove code the agent
must not see), install and build test-writer, run test-writer per flag into a
dedicated directory, then assemble `/reference`: the source language filtered
during the copy, the flagged suites under `tests/<lang>`. The host copies
`/reference` out whole and hands it to porting-harness. No host-side selection,
staging or cache key. "I think that that means the whitelist glob step can happen
in the docker container, right?"

Tests required: "the reference folder produced for the 8 conditions is what we
expect."

Spec is #72, Kevin's edit. Deletions split to #73; the porting-harness mount
question to #74; the sandbox post-copy install and its egress to #75. Closed as
superseded: #35, #52, #54, #56, #57. Closed as out of scope: PR #60 and #55.
Kevin: "we're not discussing analysis and that got tied into this migration
effort. It is wildly out of scope... It belongs to analysis. It should be thrown
away." The pipeline note PR #71 was closed in favour of the issues.

Also today: the pyodide/black warmup layer in the prepare Dockerfile was shown to
do nothing (test-writer installs black in its own process) and removed in #70;
the gbnf-experiment README gained the prepare steps in #65.
