# 2026-10-15T04:05Z — Test-configuration study queued third; one script per study

Kevin: "I'm sure that'll exhaust both remaining usage buckets but if it somehow doesn't; rerun the original experiment with test configurations as well" and "They should be two separate scripts".

Queued after the effort study: the original 16-cell study (opus-5-5, medium, every unit/source-integration/target-integration combination, both directions), n=12, under the new prompt. It resumes only from this launch's jsonls, so the two cells the models study already covers count toward n and the other 14 run fresh: 168 runs. The banked old-prompt runs in `data/runs` are not resumed. Log `internal/study_2026-10-14-testconfigs.log`.

Scripts, one per study, each idempotent: `models.fish`, `effort.fish`, `testconfigs.fish`; `chain.fish` runs them in that order and prints `CHAIN DONE`. The watchdog relaunches `chain.fish` after a usage pause.

Docs checked for the effort study (platform.claude.com effort page, code.claude.com model-config): Fable 5.1, Opus 5.5, Sonnet 5.5 and Haiku 5.5 all accept low, medium, high, xhigh and max. Claude Code never rejects a level; it clamps to the highest supported at or below. This supersedes the 03:40Z entry's "untested" note.
