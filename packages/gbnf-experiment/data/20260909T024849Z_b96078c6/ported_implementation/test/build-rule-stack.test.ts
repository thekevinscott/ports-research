import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from "../src/grammar-graph/grammar-graph-types.ts";
import { RuleRef } from "../src/grammar-graph/rule-ref.ts";
import { buildRuleStack, makeCharRule } from "../src/grammar-parser/build-rule-stack.ts";
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
  InternalRuleDefWithoutValue,
} from "../src/rules-builder/rules-builder-types.ts";

const ichar = (value: number[]) => new InternalRuleDefChar(value);
const icharAlt = (value: number) => new InternalRuleDefCharAlt(value);
const icharRngUpper = (value: number) => new InternalRuleDefCharRngUpper(value);
const icharNot = (value: number[]) => new InternalRuleDefCharNot(value);
const ialt = () => new InternalRuleDefAlt();
const iend = () => new InternalRuleDefEnd();
const iref = (value: number) => new InternalRuleDefReference(value);
const cp = (char: string) => char.codePointAt(0) as number;

describe("buildRuleStack", () => {
  it("builds a rule stack for a single path", () => {
    assert.deepEqual(buildRuleStack([ichar([120]), iend()]), [
      [new RuleChar([120]), new RuleEnd()],
    ]);
  });

  it("builds a rule stack for two alternate paths", () => {
    assert.deepEqual(
      buildRuleStack([ichar([cp("x")]), ialt(), ichar([cp("y")]), iend()]),
      [
        [new RuleChar([cp("x")]), new RuleEnd()],
        [new RuleChar([cp("y")]), new RuleEnd()],
      ],
    );
  });

  it("builds a rule stack for three alternate paths", () => {
    assert.deepEqual(
      buildRuleStack([
        ichar([cp("x")]),
        ialt(),
        ichar([cp("y")]),
        ialt(),
        ichar([cp("z")]),
        iend(),
      ]),
      [
        [new RuleChar([cp("x")]), new RuleEnd()],
        [new RuleChar([cp("y")]), new RuleEnd()],
        [new RuleChar([cp("z")]), new RuleEnd()],
      ],
    );
  });

  it("builds a rule stack for char not", () => {
    assert.deepEqual(
      buildRuleStack([icharNot([cp("x")]), ialt(), icharNot([cp("y")]), iend()]),
      [
        [new RuleCharExclude([cp("x")]), new RuleEnd()],
        [new RuleCharExclude([cp("y")]), new RuleEnd()],
      ],
    );
  });

  it("builds a rule stack for mixed char and char not", () => {
    assert.deepEqual(
      buildRuleStack([icharNot([cp("x")]), ialt(), ichar([cp("y")]), iend()]),
      [
        [new RuleCharExclude([cp("x")]), new RuleEnd()],
        [new RuleChar([cp("y")]), new RuleEnd()],
      ],
    );
  });

  it("builds a rule stack for char not with two characters and a range", () => {
    assert.deepEqual(
      buildRuleStack([
        icharNot([cp("x")]),
        icharAlt(cp("y")),
        icharAlt(cp("a")),
        icharRngUpper(cp("z")),
        iend(),
      ]),
      [
        [
          new RuleCharExclude([cp("x"), cp("y"), [cp("a"), cp("z")]]),
          new RuleEnd(),
        ],
      ],
    );
  });

  const ranges: [string, number[]][] = [
    ["[a-z]", [cp("a"), cp("z")]],
    ["[A-Z]", [cp("A"), cp("Z")]],
    ["[0-9]", [cp("0"), cp("9")]],
  ];

  for (const [grammar, [lower, upper]] of ranges) {
    it(`builds a rule stack for ${grammar}`, () => {
      assert.deepEqual(buildRuleStack([ichar([lower]), icharRngUpper(upper), iend()]), [
        [new RuleChar([[lower, upper]]), new RuleEnd()],
      ]);
    });
  }

  it("builds a rule stack for a char with a range and alternates", () => {
    assert.deepEqual(
      buildRuleStack([
        ichar([cp("a")]),
        icharRngUpper(cp("z")),
        icharAlt(cp("A")),
        icharRngUpper(cp("Z")),
        icharAlt(cp("_")),
        iend(),
      ]),
      [
        [
          new RuleChar([
            [cp("a"), cp("z")],
            [cp("A"), cp("Z")],
            cp("_"),
          ]),
          new RuleEnd(),
        ],
      ],
    );
  });

  it("builds a rule stack containing references", () => {
    assert.deepEqual(
      buildRuleStack([ichar([32]), iref(1), ialt(), iend()]),
      [
        [new RuleChar([32]), new RuleRef(1), new RuleEnd()],
        [new RuleEnd()],
      ],
    );
  });

  it("appends a trailing end rule when one is missing", () => {
    assert.deepEqual(buildRuleStack([ichar([120])]), [[new RuleChar([120]), new RuleEnd()]]);
  });

  it("throws when an alt has nothing before it", () => {
    assert.throws(() => buildRuleStack([ialt(), ichar([120]), iend()]), {
      message: "Encountered alt without anything before it",
    });
  });

  it("throws when encountering a stray char alt", () => {
    assert.throws(() => buildRuleStack([icharAlt(120), iend()]), /Encountered char alt/);
  });

  it("throws for unsupported rule types", () => {
    assert.throws(
      () => buildRuleStack([new InternalRuleDefWithoutValue() as never]),
      /Unsupported rule type/,
    );
  });
});

describe("makeCharRule", () => {
  it("builds a RuleChar for a char rule def", () => {
    assert.deepEqual(makeCharRule(ichar([97])), new RuleChar([97]));
  });

  it("builds a RuleCharExclude for a char-not rule def", () => {
    assert.deepEqual(makeCharRule(icharNot([97])), new RuleCharExclude([97]));
  });

  it("copies the rule def's value", () => {
    const ruleDef = ichar([97]);
    const rule = makeCharRule(ruleDef);
    rule.value.push(98);
    assert.deepEqual(ruleDef.value, [97]);
  });

  it("throws for an unsupported rule def", () => {
    assert.throws(
      () => makeCharRule(iref(1) as never),
      /Unsupported rule type for make_char_rule/,
    );
  });
});
