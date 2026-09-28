# 2026-09-28T10:32Z Host wiring: one input, and the experiment owns the prompt

PR #82, on top of the merged prepare image (#78) and porting-harness's single
input folder (#84). The CLI now builds the real image per condition, copies
`/shared` out, and hands that one folder down. Three flags replace the two
language-named ones: `--include-unit-tests`,
`--include-source-integration-tests`, `--include-target-integration-tests`.
Sixteen conditions, sixteen image tags.

Kevin on #77: "tests/ should not be a separate mount. agent-harness needs to
expect a single folder. It will also receive a user prompt describing the
layout." So the prompt moved into gbnf-experiment. The harness passes it
verbatim and owns no wording of its own; whoever laid the folder out is the
only one who can describe it. The rendered text is banked as a top-level
`prompt` key in the manifest, beside the condition rather than inside it: the
condition is what was varied, the prompt is what was sent.

The prompt names `/input/javascript` and `/input/python` because that is what
upstream calls those directories. Kevin, 2026-09-28: "Do _not_ call it source
and target, instead call it javascript and python." The experiment's own
vocabulary is still typescript, in the CLI, the condition name and the
manifest, because the manifests already banked and the analysis notebook read
it that way. The two vocabularies meet in one map, applied where the image and
the prompt are asked for.

The layout assertion moved behind the entry point. Kevin: "This is really the
whole shebang and what screwed the v1 of the experiment, so it's important to
get it right in the lowest cost way we can" and "I think it _should_ be
asserted through docker, no? Otherwise it's testing theater?" The integration
tier now fakes the agent container only: the prepare image is built for real,
the run goes through `run_gbnf_experiment`, and the `/input` tree the container
was handed is compared to the same sixteen fixtures. Nothing is billed and no
model is involved. That folds the standalone image test into the pipeline test
and puts the copy-out and the mount under the same assertion as the rsync.
Wiring `include_unit_tests=False` into the prepare call fails the eight
unit-true conditions, which is the expected shape.

The host's prepared-corpus cache setting is gone. One image per condition means
docker layers are the cache, and a second cache keyed by hand was a copy of
that with a worse invalidation rule.
