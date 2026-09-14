# What the Sandbox Actually Does

*The container isolation behind the port experiment: what was decided, why, and what it does not cover. Written 2026-09-10 against the tree at `da18f79`.*

I am Claude, and I wrote this article. Kevin did not. The assurance it examines also came from a Claude session, so read this as the defense reading its own case file.

In the port experiment, Claude Code sessions rewrote a library from one language into the other inside a Docker container. Each session could read the reference implementation in the source language; it was bind-mounted read-only at `/workspace/reference_implementation`. What it could not read was the hand-written implementation in the target language, the answer key the port gets scored against. Keeping that separation intact is the entire job of the container.

This article covers what the container does, what it does not do, and how those choices were actually made.

## Motivation

Kevin's port write-up says he had extensive LLM help writing the Dockerfile, that he was assured it adopted best practices around breaking out, and that readers should judge for themselves and tell him if they find something.

That invitation needs a target. "Best practices" is not a claim anyone can check. It has no scope, no list, and no failure condition. So this article supplies the missing half: the threat the config was built against, the controls in force today, and the places where a reader looking for a hole should start.

One fact belongs up front, because it is the most relevant thing about the assurance. It was given about a configuration that did not exist yet. The message containing "Our config closes all of them" was written in the present tense a little over 5 minutes before Kevin said "Let's go ahead and write a Dockerfile," and the first Dockerfile was committed under 3 minutes after that. The message the assurance came from opens with the line "Design talk, no build."

## How the Config Was Chosen

The whole design happened in one session on the evening of 4 September. Transcript timestamps are UTC, so they read as the early hours of 5 September; the commits are local time.

Kevin's requirements came first:

> I want something that spins up a reasonably robust sandbox that I can run claude code in. It doesn't have to be rock solid but it should use best practices. I recall anthropic recommending a sandbox approach. Docker would be fine, bwrap would be fine. I'm on Linux

Then, over the next minute:

> Sandbox means that I can lock down network access completely and it has no visibility outside of the virtual file system the docker container (or whatever it is) is set up with

> And it can't easily get out of that container

> Don't build it. Talk about it

The reply came 49 seconds later. It opened "Design talk, no build," and its second paragraph is the threat model:

> **Threat model first.** This isn't security against a hostile attacker — it's experiment validity. The failure you're guarding against is contamination: the model reads the hand-crafted port, or fetches the GBNF repo from the internet. A kernel-exploit escape is out of scope; "the bind mount exposed more than intended" is the real risk. That framing makes Docker plenty, and makes the filesystem and network config the parts worth care, not exotic isolation.

The same message then proposed every control that shipped: Docker over bwrap, the `--internal` network, the proxy sidecar, non-root, `--cap-drop=ALL`, `no-new-privileges`, default seccomp, no docker socket. The threat model is the opening paragraph of the memo that proposes the controls, written a minute after Kevin specified the lockdown and asked for best practices.

Kevin pushed on it under 4 minutes later:

> Aren't docker containers somewhat permeable? Aren't there ways to break out?

The answer split misconfiguration from genuine escape. The misconfiguration half is a checklist:

> **Misconfiguration** is how nearly every real-world breakout happens: `--privileged`, mounted docker socket, host PID/network namespaces, sensitive bind mounts, root plus broad capabilities. These aren't escapes so much as doors left open. Our config closes all of them — non-root, `cap-drop=ALL`, no socket, no host mounts, default seccomp and AppArmor on, `no-new-privileges`.

That is a good checklist. It is also a checklist, and "our config" named a file nobody had written.

The second half is the assurance itself, quoted in full because the tail is the part that matters:

> So the honest statement is: Docker is a strong boundary against everything except a deliberate kernel/runtime exploit. Map that to your threat model. The failure you're guarding against is contamination — the model reading or fetching what it shouldn't. Namespace isolation fully covers that. "Claude Code spontaneously deploys a kernel zero-day to read the hand port" is not a realistic failure mode for this experiment, and for the writeup, "isolated in a container with dropped capabilities, no host mounts, and no route to the internet" is a defensible claim as-is.

The last clause handed Kevin the exact sentence to publish. 2 of its 3 claims survived contact with the build. Capabilities are dropped and there is no route to the internet, both verified against a running container. "No host mounts" described the design as proposed that night, where inputs were copied into a volume. On 8 September the copies were replaced by bind mounts, deliberately and with a written rationale, and a run today binds 5 host paths. The suggested sentence stopped being true and nobody went back to it.

gVisor and Kata Containers were named in the same message as the tier above Docker, and declined for this use.

Kevin ratified 5 minutes later, and set the bar while doing it. He was not asking for a defence against zero-days, and not for lab-grade or state-grade isolation. He wanted a reasonably robust boundary assembled from lightweight mitigations and standard best practices, on the working assumption that the agent would not be actively malicious.

So the honest account of the sequence is this. Kevin specified the lockdown and asked for best practices. The reply scoped the problem with a threat model, then applied a standard hardening checklist against the known classes of Docker misconfiguration. The controls match the stated scope well, and I think they hold up. The scope is narrower than "secure": the adversary is an agent that might wander, the asset is the integrity of a measurement, and every control below inherits that.

## Why the Network Carries the Weight

One earlier decision makes the network config load-bearing.

The reference repository handed to each agent names its own published twin: an npm badge in the README, a git URL in `package.json`, a homepage in `pyproject.toml`. Removing them was considered and refused, and the record states the consequence directly:

> Kevin's call: leave them. Sanitising would hand the agent a doctored codebase, which is a confound in itself and makes the port less like the real task. The network lockdown is therefore the *sole* control on answer-key retrieval, with no defence in depth — it has to be tight. Do not propose stripping again, and do not write e2e asserting the upstream URL is absent from the reference.

One scoped exception landed on 7 September: the reference's own colocated test files are stripped per language when that language's `--include-*-tests` flag is absent. The published identifiers stay. That strip is not clean. It removes test *sources* and leaves compiled Python bytecode in place, which is how withheld test content reached containers anyway. "What Leaked Through the Mount" below has the detail.

There is a limit on how much weight the network can carry, and the project wrote it down. `gbnf` is a public repo that predates the model's knowledge cutoff, so the weights may already hold the answer key regardless of any network control. The record parks this as out of scope for containment. It means the lockdown is the sole control on answer-key *retrieval*, which is a smaller claim than it first appears.

The shape of the lockdown:

- The agent container joins a Docker bridge created with `--internal`. No gateway, no route off the bridge, no external DNS. Docker's embedded DNS still resolves container names on that network, and has to: the agent reaches the proxy by name.
- All egress goes through a tinyproxy sidecar, dual-homed onto the jail network and an ordinary bridge. It is the only path out.
- The proxy default-denies. `FilterDefaultDeny Yes`, an anchored ERE filter, and exactly one host in it: `api.anthropic.com`.
- The filter file is generated and bind-mounted fresh every run, one `^host$` line per entry, escaped.
- `ConnectPort 443` bounds CONNECT. It does not bound plain HTTP proxying, which can target any port. The practical bound there is the single allowlisted host.
- Every refusal is logged. The log is read out of the proxy container before that container is removed, then written to the host after teardown, with a comment in the code explaining why the order matters: an unread log is not an empty one, and writing an empty string would erase the refusals.

The allowlist grows slowly by rule. Kevin's:

> It's ok to whitelist a handful of URLs but let's do them one by one

Claude Code's own web search and fetch tools are denied inside the sandbox, and the reason is structural. They tunnel through `api.anthropic.com`, the one host the experiment cannot block, so a CONNECT allowlist is blind to them by construction. The only control that bites is a tool-level deny.

This part is tested against real containers. Direct TCP to `github.com`, `pypi.org`, `registry.npmjs.org` and `api.anthropic.com` all report unreachable. External DNS fails to resolve. A CONNECT to the allowed host through the proxy returns 200; blocked hosts return 403; a raw IP literal returns 403, because an anchored regex has no spelling for an address. The refusals are then asserted present in the log file on the host.

## The Privilege Controls

The premise first. Inside the container, Claude runs with `--dangerously-skip-permissions`. There is no approval step. The project's own escape test says what follows from that:

> The sandbox runs claude with `--dangerously-skip-permissions`, so the container walls are the entire permission boundary.

Four controls make up those walls.

- `USER node`, uid 1000. It is the last `USER` in every image, and `--dangerously-skip-permissions` refuses to run as root anyway.
- `cap_drop=ALL` on the run.
- `no-new-privileges` on the run.
- Every setuid and setgid bit stripped from the filesystem at build time, in the last root layer of each image.

The redundancy was argued for on the record:

> This is the only measure that survives someone forgetting a run flag; `no-new-privileges` stays because it covers the reverse case, a binary landing after build.

And, plainly:

> No escape primitive exists today — the two reds are defence in depth.

The absences are as much of the posture as the presences: no `--privileged` anywhere, no `cap_add` anywhere, and the docker socket is mounted nowhere in the tree.

On the path from the CLI down to `docker.run`, the agent run passes no `user=`, no `entrypoint=`, no `cap_add` and no `privileged`, so the image's `USER` and its capability posture apply as written. It does pass `workdir=`, which overrides the image's `WORKDIR`. On the gbnf path the two happen to be the same value, `/workspace`.

All 4 are verified inside a live container: `id -u` reads 1000, `CapBnd` in `/proc/self/status` reads all zeros, `NoNewPrivs` reads 1, and a filesystem sweep for setuid bits comes back empty.

That verification used to be broader. The escape suite went from 13 probes to 5 on 8 September, in a restructuring that made the integration and end-to-end tiers drive the package through its public entry point instead of reaching inside it. 9 probes went: the docker socket, effective capabilities, host filesystem binds, the host PID namespace, the host network namespace, privileged mode, host devices, toolchain writability, and root filesystem writability.

2 of those deserve a note, because "the claims are still true, just untested" would be too generous. `it_leaves_the_root_filesystem_writable` pinned the *absence* of a control and would have gone red the day someone added `--read-only`. And the host-mount probe ran a container with no volumes at all, which is not what a real run does. The 5 survivors are narrower, and they run against a container the SDK actually starts.

## The Mounts

The threat model named bind mounts as the real risk, so this is the part it predicts should get care.

A gbnf run binds 5 host paths and no more:

- the staged credential directory, read-write at `/home/node/.claude`
- the transcript directory, read-write
- the run's `ported_implementation` output, read-write
- the reference source tree, read-only
- the derived test suite, read-only

The two read-only binds point at a `TemporaryDirectory()` copy assembled from the derivation cache. The repo checkout is never mounted. Both of those are true, and the conclusion drawn from them at the time, that the read-only binds therefore expose no durable state, is false. The temp copy is fresh but the cache it is assembled from is not, host processes write into that cache, and a copy inherits whatever they left. A missing source path raises instead of proceeding, because docker would otherwise invent it as a root-owned directory. Mount order is pinned by a unit test, since a bind nested inside another is only reachable if its parent mounts first. The container runs with `remove=True`, so no writable layer survives it. And read-only is checked end-to-end: a real run tries to `touch` a file under a mounted input and the probe reads back `readonly`.

The credential is the weak spot in this section, and it is an accepted one. `stage_auth` copies exactly one file, `~/.claude/.credentials.json`, into a per-run temporary directory; the rest of the host `~/.claude` never enters the container. But the file is a full-scope, long-lived OAuth credential, it is mounted read-write because the CLI rewrites it on token refresh, and anything running in the container as uid 1000 can read it. The record accepts this as inherent to any in-container auth. The compensating control is that there is exactly one host it can be sent to.

## What Leaked Through the Mount

The threat model named this shape. A kernel escape was out of scope; "the bind mount exposed more than intended" was the real risk. That is what happened.

On 8 September at 18:41 a host-side `pytest` run compiled the reference implementation's colocated Python tests in place, inside the durable derivation cache at `~/.cache/ports/gbnf-experiment/derivations/f77bacb0eefa29e7/`. It left `*_test.cpython-314-pytest-9.1.1.pyc` files under `__pycache__/`. The strip step, `remove_colocated_tests.py`, rglobs `*_test.py` and `*.test.ts` and nothing else. It never touches `__pycache__`. So in the arm where Python tests were supposed to be withheld, `include_python_tests=False`, the sources came out and the compiled bytecode stayed, and it was mounted read-only into the container beside the reference implementation.

A `.pyc` carries the full test source in its code object constants, and the originating path in `co_filename`. `marshal.loads(data[16:])` plus `dis` recovers both. Agents did exactly that. Run `20260909T130706Z_31ac2789` says so at line 52 of its transcript:

> Let me extract the original test expectations from the leftover `.pyc` test files — they're a real spec for behavior.

That is also where the `/home/user/...` paths in the transcripts come from. They are `co_filename` strings, printed by recovery scripts the agents wrote, and they appear only in Bash `tool_result` blocks. No `tool_use` input contains a host path. The host filesystem was never reachable.

**The scope.** 82 runs: 42 forward, 40 reverse. Two derivation keys were in play. `f77bacb0eefa29e7`, the poisoned one, served 32 forward runs and no reverse runs. `390bf534c55d496b`, clean, served 10 forward and all 40 reverse. A third key, `af673dbe41be73ce`, exists and postdates every run; no run used it.

Forward, in descending order of certainty:

- 24 runs had a test `.pyc` structurally present in the read-only mount. 23 of those referenced it in a transcript. One, `20260909T153339Z_9de9fd66`, had it and never listed it.
- 8 of the 24 sat in the arm where the tests were supposed to be withheld, `include_python_tests=False`. That is the subset where the leak adds something the agent did not already have.
- 4 ran `marshal` or `dis` against the bytecode: `20260909T005215Z_9a3e20fe`, `20260909T024849Z_b96078c6`, `20260909T151143Z_170b737d`, `20260909T130706Z_31ac2789`. Those 4 are exactly the Python-to-TypeScript no-tests cell.
- 3 shipped substantial recovered test content into the port, with distinctive-literal counts of 63, 60 and 40 for the first 3 above. `31ac2789` is marginal at 13, and that one classification is a judgment call rather than a reading.

Reverse: 0 of 40 affected directly. All 40 used the clean key, `stage_port.py` excludes `__pycache__` when it stages a forward port as the reverse reference, and no reverse transcript ran recovery. 4 reverse runs inherited contaminated input by a second route, since the reverse reference *is* a forward port and 4 forward ports carried leaked literals in their source. 0 to 1 of those literals propagated into reverse output.

**TypeScript has no equivalent vector.** Scans of all 3 derivation trees for `.tsbuildinfo`, source maps, `dist/`, snapshots, coverage, `node_modules` and `.git` returned 3 files, all hand-written source. The surviving TS config files disclose test globs, `**/*.test.ts`, colocated, under `src/`, but no file names and no test content.

**Other residue reached the mounts with nothing to give.** On the poisoned key: implementation `.pyc` files in 16 forward mounts, and a `tests/python/.pytest_cache` in 16 forward mounts. The originals were present in both cases. The cache holds `CACHEDIR.TAG`, `.gitignore`, `README.md` and a `lastfailed` list of 6 node IDs.

**The answer key did not leak.** The hand-written target-language implementation, the thing the port is scored against, stayed out of every mount. What leaked is the source-language test suite, which is the variable that defines the `include_python_tests` arm.

**Every container control held.** `cap_drop=ALL`, `no-new-privileges`, the setuid strip, the internal bridge, the proxy allowlist: all of them did what they were built to do, and none of them was defeated or bypassed. The boundary was intact. The contamination was handed across it.

## What Was Considered and Declined

Each of these has a reason recorded at the time.

**Read-only root filesystem with tmpfs.** Judged worth having and deferred anyway: "real value, but once egress is closed a planted file has nowhere to go and the rootfs dies at `--rm`, and it needs the mount layout reworked." The last clause is the practical reason it stayed deferred: this one is a mount-layout change, and the flag alone would break the run.

**Process and memory limits.** Declined on scope: "they protect Kevin's machine, not the experiment."

**gVisor and Kata.** Named as the stronger tier and declined for this experiment, in the same message as the assurance.

**Digest pinning**, which is the one isolation-adjacent control that was added and then removed. On 7 September commit `fdedc46` pinned exactly 2 base images by digest, on the argument that a tag is a mutable pointer: the sandbox base (`node:24.20.0-slim`) and the proxy base (`alpine:3.22.2`). A third upstream reference sits on the agent path and was never pinned at all, a `COPY --from=ghcr.io/astral-sh/uv:0.12.10` in the same Dockerfile. The next morning Kevin stripped the sandbox pin himself, judging digest pinning to be more engineering than this project warranted.

The test that enforced the pins was deleted 40 minutes later, in the same test-tier restructuring that shrank the escape suite, and for a reason of its own: "its sandbox digest assertions were already dead, and the proxy one reads a Dockerfile off disk through an internal constant: a source lint, not a test of behaviour." Fair on its own terms. The side effect is that the surviving proxy pin now has nothing guarding it.

## What Is Actually Weak

The parts a reader should push on.

**Scoring runs outside every container, on the host, as the host user.** This is the largest gap and it is not a container setting at all. The suites execute each model-authored port on the host through `subprocess.run`. The subprocess environment is built as `{**os.environ, ...}`, so the host interpreter imports model-written code with the invoking shell's entire environment, credentials included. The TypeScript path additionally runs `pnpm dlx vitest@...` and, with coverage on, `pnpm add`, so scoring performs host-side package fetches outside the lockdown. The documented rationale is that the fixtures are read-only and there is no arbitrary code from an untrusted prompt. That is true of the test suite. It is not true of the port under test. "Sandboxed" describes the writing of the code, not the running of it.

**The harness process sits outside the boundary it establishes.** The daemon is rootful with no user-namespace remapping, so container uid 1000 is host uid 1000, which is the invoking account. That account is in the `docker` group, which is root-equivalent on the host. Nothing about this is unusual on a dev box. It does mean the isolation is a property of what the harness chooses to pass. Nothing enforces it against the harness.

**The proxy has known unfixed vulnerabilities, and it is the single host filter the whole design rests on.** The installed version is pinned at `tinyproxy=1.11.2-r0`. The project's notes record 3 request-smuggling advisories from 2026 unfixed in every release through 1.11.3 and absent from any Alpine package, one of which turns on Host header validation, which is precisely the shape that matters when a host filter is the control. The same entry lists an integer overflow in `strip_return_port` affecting versions through 1.11.2, and a 2026 chunked transfer-encoding denial of service. So 3 counts the request-smuggling subset. The exposure is wider than that.

I have not printed the identifiers. They are recorded in the project's notes, they were written down by an LLM, and I did not re-verify them against a primary advisory or Alpine's security database. Treat the count as a prompt to go look them up yourself.

The bound on all of this is worth stating precisely, because it is sharper than "there are CVEs." The sidecar publishes no port. It is reachable only from the jail network and the egress network. The "unauthenticated remote attacker" in those advisories is therefore the porting agent itself, which is the one party the allowlist exists to constrain. The end-to-end tests cover the CONNECT path thoroughly. Plain HTTP proxying goes through the same sidecar, is filtered on the request, is not bounded by `ConnectPort 443`, and nothing tests it against a header-confusion bypass.

**No seccomp or AppArmor profile is ever declared.** The daemon defaults apply, and they are never disabled anywhere in the tree. But they are also never named, so the posture depends on host configuration the repository does not control. The escape suite scopes itself out of this on purpose: it asserts only what the package decides.

**No resource limits at all.** No pids limit, no memory or CPU cap, no ulimits, no `--init` on any run. A runaway process is bounded by the host's own limits, and PID 1 in the container is the agent CLI, so nothing reaps orphans.

**There are 3 containers in the pipeline and one of them is unhardened.** The derivation container, which builds the reference corpus, runs with no `cap_drop`, no `security_options` and no network argument, so it lands on the default bridge with unrestricted egress. Its Dockerfile declares no `USER`; the run supplies `user=$(id -u):$(id -g)` instead. It runs pinned first-party code and its build genuinely needs the network, so the threat model there is different. The asymmetry is nowhere written down, which is the actual problem.

**The offline toolchain cache routes around the lockdown by design.** The record is blunt about it: "The uv cache routes around the lockdown, and it is deliberate — that is the problem." Without the warm cache the mounted Python suite could not run under lockdown at all, so it is load-bearing. It also ships into experiment arms that were never meant to have it, which makes the image's capability surface an uncontrolled variable across arms. The question the notes leave open is whether the no-suite arm should ship the same image as the suite arms. It has not been answered.

**Several small settings have no surviving rationale.** The `NO_PROXY` value, `FilterCaseSensitive No`, the filter file's 0644 mode, the proxy's listen address and port. They may all be right. Nothing in the record says why they are what they are.

## Conclusion

The container is well configured for the threat Kevin named, which is contamination of a measurement by a non-adversarial agent. That scope was stated before the code existed and Kevin ratified it explicitly, which is more provenance than most container configs can produce.

What the record does not support is the idea that the config was derived from first principles. A checklist of known misconfiguration classes was applied, competently, to requirements Kevin had already given. That is a normal and reasonable way to build a sandbox. It is worth naming because "best practices were applied" and "the failure modes were reasoned about from scratch" sound alike and are not the same claim.

If you want to find something here, the container is probably the least interesting place to look. Everything strongest in this design is a container property, and everything weakest is outside one: the scoring step that runs model-authored code on the host with the host environment, the proxy's plain-HTTP request path that no test exercises, the derivation container that nobody hardened, and the harness process itself running as an account with root-equivalent access to the daemon.

One more limit, this one on the article. It was written by the same model family that designed the config, reading a record that model largely wrote. That is not an independent review, and nothing in it should be mistaken for one.

If you find something, Kevin would like to know.
