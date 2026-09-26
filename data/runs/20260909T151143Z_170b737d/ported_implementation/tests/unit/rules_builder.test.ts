import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { GrammarParseError } from "../../src/utils/errors/index.ts";
import { KeyError } from "../../src/utils/python_compat.ts";
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
} from "../../src/rules_builder/rules_builder_types.ts";
import { RulesBuilder, get_out_elements } from "../../src/rules_builder/rules_builder.ts";
import { SymbolIds } from "../../src/rules_builder/symbol_ids.ts";

describe("SymbolIds", () => {
  it("stores values, positions and the reverse mapping", () => {
    const symbol_ids = new SymbolIds();
    symbol_ids.set("root", 0, 4);
    assert.equal(symbol_ids.length, 1);
    assert.ok(symbol_ids.has("root"));
    assert.equal(symbol_ids.getItem("root"), 0);
    assert.equal(symbol_ids.get_pos("root"), 4);
    assert.equal(symbol_ids.reverse_get(0), "root");
    assert.deepStrictEqual([...symbol_ids], [["root", 0]]);
  });

  it("throws for unknown keys and values", () => {
    const symbol_ids = new SymbolIds();
    assert.throws(() => symbol_ids.getItem("root"), KeyError);
    assert.throws(() => symbol_ids.get_pos("root"), /does not contain key: root/);
    assert.throws(() => symbol_ids.reverse_get(0), /does not contain value: 0/);
  });
});

describe("get_out_elements", () => {
  it("builds the requested rule definition", () => {
    assert.deepStrictEqual(
      get_out_elements(InternalRuleDefChar, 97),
      new InternalRuleDefChar([97]),
    );
    assert.deepStrictEqual(
      get_out_elements(InternalRuleDefCharNot, 97),
      new InternalRuleDefCharNot([97]),
    );
    assert.deepStrictEqual(
      get_out_elements(InternalRuleDefCharRngUpper, 97),
      new InternalRuleDefCharRngUpper(97),
    );
    assert.deepStrictEqual(get_out_elements(InternalRuleDefAlt, 0), new InternalRuleDefAlt());
    assert.deepStrictEqual(get_out_elements(InternalRuleDefEnd, 0), new InternalRuleDefEnd());
    assert.deepStrictEqual(
      get_out_elements(InternalRuleDefCharAlt, 97),
      new InternalRuleDefCharAlt(97),
    );
  });
});

describe("rule definition equality", () => {
  it("compares by class and value, like the reference's __eq__", () => {
    assert.ok(new InternalRuleDefChar([97]).equals(new InternalRuleDefChar([97])));
    assert.ok(new InternalRuleDefEnd().equals(new InternalRuleDefEnd()));
    assert.ok(!new InternalRuleDefEnd().equals(new InternalRuleDefAlt()));
    assert.ok(!new InternalRuleDefChar([97]).equals(new InternalRuleDefCharNot([97])));
    assert.ok(!new InternalRuleDefCharAlt(97).equals(new InternalRuleDefCharAlt(98)));
  });
});

describe("RulesBuilder", () => {
  it("builds a literal rule", () => {
    const builder = new RulesBuilder('root ::= "foo"');
    assert.deepStrictEqual(builder.rules, [
      [
        new InternalRuleDefChar([102]),
        new InternalRuleDefChar([111]),
        new InternalRuleDefChar([111]),
        new InternalRuleDefEnd(),
      ],
    ]);
    assert.deepStrictEqual([...builder.symbol_ids], [["root", 0]]);
  });

  it("builds a rule that references another rule", () => {
    const builder = new RulesBuilder('root ::= foo\nfoo ::= "bar"');
    assert.deepStrictEqual(
      [...builder.symbol_ids],
      [
        ["root", 0],
        ["foo", 1],
      ],
    );
    assert.deepStrictEqual(builder.rules[0], [
      new InternalRuleDefReference(1),
      new InternalRuleDefEnd(),
    ]);
  });

  it("expands a character class into alts and range uppers", () => {
    const builder = new RulesBuilder("root  ::= [a-zA-Z0-9]");
    assert.deepStrictEqual(builder.rules, [
      [
        new InternalRuleDefChar([97]),
        new InternalRuleDefCharRngUpper(122),
        new InternalRuleDefCharAlt(65),
        new InternalRuleDefCharRngUpper(90),
        new InternalRuleDefCharAlt(48),
        new InternalRuleDefCharRngUpper(57),
        new InternalRuleDefEnd(),
      ],
    ]);
  });

  it("generates a sub-rule for a modifier", () => {
    const builder = new RulesBuilder('root  ::= "f"*');
    assert.deepStrictEqual(
      [...builder.symbol_ids],
      [
        ["root", 0],
        ["root_1", 1],
      ],
    );
    assert.deepStrictEqual(builder.rules[1], [
      new InternalRuleDefChar([102]),
      new InternalRuleDefReference(1),
      new InternalRuleDefAlt(),
      new InternalRuleDefEnd(),
    ]);
  });

  it("reports an undefined rule identifier", () => {
    assert.throws(
      () => new RulesBuilder("root ::= foo"),
      (error: unknown) => {
        assert.ok(error instanceof GrammarParseError);
        assert.equal(
          error.message,
          'Failed to parse grammar: Undefined rule identifier "foo"\n\nroot ::= foo\n         ^',
        );
        return true;
      },
    );
  });

  it("reports a missing ::=", () => {
    assert.throws(() => new RulesBuilder("root"), /Expecting ::= at 4/);
  });

  it("reports a modifier with nothing before it", () => {
    assert.throws(() => new RulesBuilder("root ::= *"), /Expecting preceding item to \*\/\+\/\?/);
  });

  it("reports an unclosed group", () => {
    assert.throws(() => new RulesBuilder('root ::= ("foo"'), /string index out of range/);
  });

  it("enforces the parse time limit", () => {
    const builder_with_no_time = () => {
      const builder = new RulesBuilder('root ::= "f"');
      builder.time_limit = -1;
      builder.check_duration();
    };
    assert.throws(builder_with_no_time, /Duration of -1 exceeded/);
  });
});
