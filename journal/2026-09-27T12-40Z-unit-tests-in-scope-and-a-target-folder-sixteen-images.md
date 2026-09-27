# 2026-09-27T12:40Z unit tests in scope, and a target folder: sixteen images

Follows the 12:10Z entry, which left unit tests open. Kevin: "I know unit
tests are out of scope today; I'm proposing bringing them into scope."

## Unit tests

Upstream has 31 colocated `*.test.ts` under `src/` and 22 colocated
`*_test.py` under `gbnf/`, each importing its siblings by relative path, each
runnable with the shipped config. They pin structure where the integration
suites pin behaviour, which is the axis a clone-versus-reimplement study wants.

They are source-language only. The other language's unit tests would hand
the agent the module layout of the implementation it is supposed to arrive
at, which is a different question and one only a repo with two
implementations can ask. So one new build arg, `INCLUDE_UNIT_TESTS`, applying
to the source package. Source language, unit, python integration, typescript
integration: sixteen images. Kevin: "Yes. 16 images."

## The target folder

Kevin: "We already have /source/<lang> - this _always_ contains the source for
a package, plus it may also contain unit tests, plus it may _also_ contain
integration tests. Both those tests, if included, stay where they are (i.e.,
they match where they currently live today). We could copy this pattern and
have /target/<lang> and have the tests exist in the same layout, sans the
source code."

Adopted. `/reference/source/<lang>` is the source package in upstream layout,
with whichever of its tests the flags allow left in place.
`/reference/target/<lang>` is the other language, present only when its
integration flag is on: the generated suite in upstream layout plus the files
upstream runs it with, and no source. One mechanism for both, an rsync
whitelist over the upstream package with a different composition of rule
files. The lifted `/reference/tests/<lang>` is gone, and so is the invented
vitest config that lived there.

On whether the image should wire the target tests up for the agent, Kevin:
"the agent, as part of writing, can copy those into its reference
implementation, yes? I don't know that it's more helpful to try to configure
the /target folder for them vs. just providing them to look at." Provided to
look at. PR #78.
