# 2026-09-27T12:10Z tests are open-book and stay where upstream puts them

Kevin, going through PR #78 line by line, on what the reference tests are for
and how a porting agent should get them. Supersedes the test half of the
2026-09-26T23:55Z entry: suites are generated regardless of flag, and tests are
no longer lifted to `/reference/tests` when they can stay in place.

## The framing

Two prongs. "For GBNF, we are studying the effects of including or excluding
tests (either unit, integration, or both), so we _do_ want to maintain that
control. For a v3 future experiment, with additional repos, we will _not_ be
taking that path." The approach has to be "fairly generic and adaptable to all
manner of repos", which gives two constraints:

1. "We shouldn't make any assumptions about how test suites are _organized_;
   other suites may not have the unit / integration test suite division that
   GBNF has."
2. "It is not feasible that for each repo we will 'fix' or otherwise patch a
   working test environment, beyond the one that already ships with the repo.
   We may have 100s of repos under test and therefore, the tests either work
   or they do not."

## Decisions

- **Tests are open-book.** Across repos the tests are in the source language
  and cannot run against a port in another language. If the agent wants an
  oracle it ports the tests too; that is part of the task, not something the
  image supplies. GBNF's cross-language generated suites (test-writer emits
  both languages from one markdown corpus) make "runnable target-language
  tests provided" a condition that exists only for GBNF, and findings from it
  do not transfer.
- **Ship the repo's own harness, never an invented one.** The configs,
  Makefile, and whatever upstream runs the suite with come along as they are.
  Whether the suite runs in the sandbox is a measured fact about the repo.
  The scaffolding `vitest.config.unit.ts` in the prepare image (a made-up
  config that ran the lifted integration suite with an alias to the port)
  was a repair, and repairs do not scale. It is deleted.
- **Same-language tests stay where upstream puts them.** Typescript source
  with typescript tests keeps the unit tests colocated under `src/` and the
  generated integration tests under `integration-tests/generated/`, inside
  `/reference/source`, next to the configs that run them. Same for python.
  Cross-language tests have no home in the shipped package and are lifted to
  `/reference/tests/<lang>`; they are open-book only.
- **Unit versus integration is classified by what a test imports**, not by
  the repo's naming: public entry point constrains behaviour, internal paths
  constrain structure. For GBNF that maps onto the existing split. A repo
  without the split collapses the condition, and the record says so.

## Open

The prepare image's build args select the language of the generated
integration tests. The filter rules drop `*.test.ts` and `*_test.py`
unconditionally, so no image today carries unit tests. The control Kevin
named (unit, integration, or both) is a different axis and is not yet
encoded. Either it becomes a build arg and more than eight images, or the
docs stop implying the unit half exists.
