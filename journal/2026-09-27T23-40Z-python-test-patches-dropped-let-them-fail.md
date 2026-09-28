# 2026-09-27T23:40Z python test patches dropped: let them fail

Follows the 23:14Z entry. PR #78 had accumulated three patches to make the
python integration suite match typescript's: a template for `grammars.md`,
two fixes inside test-writer, and a Makefile that writes every suite. The
last round replaced a fixture copy with inlined grammars and, in doing so,
found a second test-writer fault that had been dropping escaped newlines from
three shipped python grammars since the pin.

Kevin: "we've been wrestling this for approaching a week now. I feel very
uncomfortable with all this mucking about with source. I'd prefer that we
build it up after we see it in action. I think I'd like to propose deleting
all patches related to patching the python integration tests. Let them fail.
Let's see them fail, and let's fix them when they fail and we can see how
they fail."

All three are gone. One patch remains, the builder re-export removal, which
is about the filtered source typechecking and not about tests. The python
package generates the five suites its Makefile names at the pin, with
whatever test-writer does to them, and `grammars.md` has no python suite. The
sixteen listings lose `grammars_test.py` and the grammar fixture files. The
findings above stay on record in the PR history for when a run shows how the
suite fails.
