import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { build_rule_stack } from "../../src/grammar_parser/build_rule_stack.ts";
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
} from "../../src/grammar_graph/grammar_graph_types.ts";
import { RuleRef } from "../../src/grammar_graph/rule_ref.ts";
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
} from "../../src/rules_builder/rules_builder_types.ts";

const cp = (value: string | number): number =>
  typeof value === "number" ? value : (value.codePointAt(0) as number);

const ichar = (value: number[]) => new InternalRuleDefChar(value);
const ichar_alt = (value: number) => new InternalRuleDefCharAlt(value);
const ichar_rng_upper = (value: number) => new InternalRuleDefCharRngUpper(value);
const ichar_not = (value: number[]) => new InternalRuleDefCharNot(value);
const ialt = () => new InternalRuleDefAlt();
const iend = () => new InternalRuleDefEnd();
const iref = (value: number) => new InternalRuleDefReference(value);
const make_range = (lower: string | number, upper: string | number): Range => [
  cp(lower),
  cp(upper),
];

describe("build_rule_stack", () => {
  it("builds a rule stack for a single path", () => {
    assert.deepStrictEqual(build_rule_stack([ichar([120])]), [
      [new RuleChar([120]), new RuleEnd()],
    ]);
  });

  it("builds a rule stack for two alternate paths", () => {
    assert.deepStrictEqual(
      build_rule_stack([ichar([cp("x")]), ialt(), ichar([cp("y")])]),
      [
        [new RuleChar([cp("x")]), new RuleEnd()],
        [new RuleChar([cp("y")]), new RuleEnd()],
      ],
    );
  });

  it("builds a rule stack for three alternate paths", () => {
    assert.deepStrictEqual(
      build_rule_stack([
        ichar([cp("x")]),
        ialt(),
        ichar([cp("y")]),
        ialt(),
        ichar([cp("z")]),
      ]),
      [
        [new RuleChar([cp("x")]), new RuleEnd()],
        [new RuleChar([cp("y")]), new RuleEnd()],
        [new RuleChar([cp("z")]), new RuleEnd()],
      ],
    );
  });

  it("builds a rule stack for char-not", () => {
    assert.deepStrictEqual(
      build_rule_stack([
        ichar_not([cp("x")]),
        ialt(),
        ichar_not([cp("y")]),
        ialt(),
        ichar_not([cp("z")]),
      ]),
      [
        [new RuleCharExclude([cp("x")]), new RuleEnd()],
        [new RuleCharExclude([cp("y")]), new RuleEnd()],
        [new RuleCharExclude([cp("z")]), new RuleEnd()],
      ],
    );
  });

  it("builds a rule stack for mixed char and char-not", () => {
    assert.deepStrictEqual(
      build_rule_stack([
        ichar_not([cp("x")]),
        ialt(),
        ichar([cp("y")]),
        ialt(),
        ichar_not([cp("z")]),
      ]),
      [
        [new RuleCharExclude([cp("x")]), new RuleEnd()],
        [new RuleChar([cp("y")]), new RuleEnd()],
        [new RuleCharExclude([cp("z")]), new RuleEnd()],
      ],
    );
  });

  it("builds a rule stack for char-not with two characters and a range", () => {
    assert.deepStrictEqual(
      build_rule_stack([
        ichar_not([cp("x")]),
        ichar_alt(cp("y")),
        ichar_alt(cp("z")),
        ichar_rng_upper(130),
      ]),
      [
        [
          new RuleCharExclude([cp("x"), cp("y"), [cp("z"), 130]]),
          new RuleEnd(),
        ],
      ],
    );
  });

  describe("modifiers", () => {
    const cases: Array<[string, ReturnType<typeof ichar>[], unknown]> = [
      [
        "[a-z]?",
        [ichar([cp("a")]), ichar_rng_upper(cp("z")), ialt(), iend()] as never,
        [[new RuleChar([make_range("a", "z")]), new RuleEnd()], [new RuleEnd()]],
      ],
      [
        "[a-zA-Z]?",
        [
          ichar([cp("a")]),
          ichar_rng_upper(cp("z")),
          ichar_alt(cp("A")),
          ichar_rng_upper(cp("Z")),
          ialt(),
          iend(),
        ] as never,
        [
          [
            new RuleChar([make_range("a", "z"), make_range("A", "Z")]),
            new RuleEnd(),
          ],
          [new RuleEnd()],
        ],
      ],
      [
        "[a-z]+",
        [
          ichar([cp("a")]),
          ichar_rng_upper(cp("z")),
          iref(1),
          ialt(),
          ichar([cp("a")]),
          ichar_rng_upper(cp("z")),
          iend(),
        ] as never,
        [
          [new RuleChar([make_range("a", "z")]), new RuleRef(1), new RuleEnd()],
          [new RuleChar([make_range("a", "z")]), new RuleEnd()],
        ],
      ],
      [
        "[a-z]*",
        [
          ichar([cp("a")]),
          ichar_rng_upper(cp("z")),
          iref(1),
          ialt(),
          iend(),
        ] as never,
        [
          [new RuleChar([make_range("a", "z")]), new RuleRef(1), new RuleEnd()],
          [new RuleEnd()],
        ],
      ],
    ];

    for (const [grammar, input, expected] of cases) {
      it(grammar, () => {
        assert.deepStrictEqual(build_rule_stack(input), expected);
      });
    }
  });

  it("appends a trailing end rule when the path does not have one", () => {
    assert.deepStrictEqual(build_rule_stack([iref(3)]), [[new RuleRef(3), new RuleEnd()]]);
  });

  it("throws when an alt has nothing before it", () => {
    assert.throws(
      () => build_rule_stack([ialt(), ichar([cp("x")])]),
      /Encountered alt without anything before it/,
    );
  });

  it("does not mutate the incoming rule definitions", () => {
    const char_def = ichar([cp("a")]);
    build_rule_stack([char_def, ichar_rng_upper(cp("z")), iend()]);
    assert.deepStrictEqual(char_def.value, [cp("a")]);
  });
});
