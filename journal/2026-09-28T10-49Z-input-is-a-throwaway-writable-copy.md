# 2026-09-28T10:49Z /input is a throwaway writable copy

The one input folder mounted read-only at `/input`, which read the intent of
#77 as a read-only container path. Kevin: "'input' is not meant to be
read-only ... It is meant to be _non-synced_; that doesn't imply that the
folder within the container is read only, only that changes made do not get
reflected to the host system." A bind mount is two-way, so non-synced means
the container needs its own copy.

The sandbox now copies the input folder into a staging directory inside the
run's temporary context and mounts that copy writable at `/input`. The copy
goes when the context exits. The agent can install dependencies and scratch
under `/input`; nothing it writes reaches the caller's folder. The existence
and is-a-directory checks moved ahead of the copy. Outputs and the transcripts
mount are unchanged: those are still the caller's own directories, bound so
what the container writes survives.

Unit and integration suites went red first — the old tests asserted the source
was the caller's folder and the mode was `ro` — then green: 137 unit, 21
integration. A new integration test has the fake container write into the
`/input` source and asserts the caller's folder is unchanged afterwards.
