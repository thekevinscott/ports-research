# 2026-09-28T01:05Z Prepare image: one rsync, upstream layout, three rule files per language

PR #78, commit f9ea450. The prepare image's copy step is now a single `rsync`
of `packages/gbnf/` into `/shared/`, driven by one build arg, `RULES`.

Kevin: "What I want is a single rules file describing the whitelist. I
understand that we have two separate runs to produce a source and a target.
What if instead we just maintain the layout as it exists on disk. Do _not_
call it source and target, instead call it javascript and python. Then we
could get it down to a single rsync, yes?"

Every rule is anchored to `/python/` or `/javascript/`, so one filter covers
both trees and a language with no lines gets no files. `/shared` mirrors
upstream: `python/` and `javascript/`, only the whitelisted files. The corpus
no longer says which language is the source.

Kevin: "the reference filters - they can go down to three for each language,
right?" `harness.rules` folded into `integration-tests.rules`: the suite is
useless without its runner, and duplicate lines against `source.rules` are
harmless under first-match. Three files per language: `source`,
`unit-tests`, `integration-tests`.

Built by hand at pin 13f1aca: python all-on, python all-off, javascript
all-on. Trees as designed; exclusions of `dev/`, `src/builder/` and
`node_modules/` held.

For #82: the host calls `assemble_whitelist` and passes `RULES`; expects
`/shared/{python,javascript}`; the prepare cache key must fold in the rules
text, since the rule files left the docker directory it digests.
