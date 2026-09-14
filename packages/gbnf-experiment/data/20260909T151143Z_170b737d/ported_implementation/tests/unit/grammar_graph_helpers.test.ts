import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { Color, colorize } from "../../src/grammar_graph/colorize.ts";
import { get_input_as_code_points } from "../../src/grammar_graph/get_input_as_code_points.ts";
import { get_parent_stack_id } from "../../src/grammar_graph/get_parent_stack_id.ts";
import {
  KEY_TRANSLATION,
  get_serialized_rule_key,
} from "../../src/grammar_graph/get_serialized_rule_key.ts";
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type UnresolvedRule,
} from "../../src/grammar_graph/grammar_graph_types.ts";
import { GraphNode } from "../../src/grammar_graph/graph_node.ts";
import { GraphPointer } from "../../src/grammar_graph/graph_pointer.ts";
import { RuleRef } from "../../src/grammar_graph/rule_ref.ts";

describe("colorize", () => {
  it("colorizes strings", () => {
    assert.equal(colorize("hello", Color.BLUE), "\x1b[34mhello");
    assert.equal(colorize("test", Color.CYAN), "\x1b[36mtest");
    assert.equal(colorize("example", Color.GREEN), "\x1b[32mexample");
  });

  it("colorizes numbers", () => {
    assert.equal(colorize(123, Color.RED), "\x1b[31m123");
    assert.equal(colorize(456, Color.GRAY), "\x1b[90m456");
    assert.equal(colorize(789, Color.YELLOW), "\x1b[33m789");
  });
});

describe("get_input_as_code_points", () => {
  it("returns code points for a string", () => {
    assert.deepStrictEqual(get_input_as_code_points("abc"), [97, 98, 99]);
  });

  it("returns code points for a number", () => {
    assert.deepStrictEqual(get_input_as_code_points(99), [99]);
  });

  it("returns code points for an array of numbers", () => {
    assert.deepStrictEqual(get_input_as_code_points([99, 100, 101]), [99, 100, 101]);
  });

  it("treats astral characters as a single code point", () => {
    assert.deepStrictEqual(get_input_as_code_points("\u{1F4A9}"), [128169]);
  });

  it("rejects an array holding a non-integer", () => {
    assert.throws(
      () => get_input_as_code_points(["a"] as unknown as number[]),
      /code_point must be an integer/,
    );
  });
});

describe("RuleRef", () => {
  it("initializes with a given value", () => {
    assert.equal(new RuleRef(123).value, 123);
  });

  it("allows setting and getting nodes", () => {
    const mockNodes = new Set<GraphNode>();
    const ruleRef = new RuleRef(123);
    ruleRef.nodes = mockNodes;
    assert.equal(ruleRef.nodes, mockNodes);
  });

  it("throws if nodes are read before being set", () => {
    const ruleRef = new RuleRef(123);
    assert.throws(() => ruleRef.nodes, /Nodes are not set/);
  });
});

describe("rule equality", () => {
  it("compares by class and value, like the reference's __eq__", () => {
    assert.ok(new RuleEnd().equals(new RuleEnd()));
    assert.ok(new RuleChar([97]).equals(new RuleChar([97])));
    assert.ok(new RuleChar([[97, 122]]).equals(new RuleChar([[97, 122]])));
    assert.ok(new RuleRef(1).equals(new RuleRef(1)));

    assert.ok(!new RuleChar([97]).equals(new RuleChar([98])));
    assert.ok(!new RuleChar([97]).equals(new RuleCharExclude([97])));
    assert.ok(!new RuleEnd().equals(new RuleChar([97])));
    assert.ok(!new RuleRef(1).equals(new RuleRef(2)));
  });

  it("copies the incoming value so callers cannot mutate a rule through it", () => {
    const value = [97];
    const rule = new RuleChar(value);
    value.push(98);
    assert.deepStrictEqual(rule.value, [97]);
  });
});

describe("get_serialized_rule_key", () => {
  it("returns the type for end rules", () => {
    assert.equal(get_serialized_rule_key(new RuleEnd()), `${KEY_TRANSLATION.get(RuleEnd)}`);
  });

  it("returns the type and value for character rules", () => {
    assert.equal(
      get_serialized_rule_key(new RuleChar([97])),
      `${KEY_TRANSLATION.get(RuleChar)}-[97]`,
    );
  });

  it("serializes ranges with Python's spacing", () => {
    assert.equal(get_serialized_rule_key(new RuleChar([[97, 122]])), "1-[[97, 122]]");
  });

  it("returns the type and value for character exclude rules", () => {
    assert.equal(
      get_serialized_rule_key(new RuleCharExclude([97])),
      `${KEY_TRANSLATION.get(RuleCharExclude)}-[97]`,
    );
  });

  it("returns the ref type with value for reference rules", () => {
    assert.equal(get_serialized_rule_key(new RuleRef(99)), "3-99");
  });

  it("throws for unknown rule types", () => {
    const rule = { type: "UNKNOWN", value: "something" } as unknown as UnresolvedRule;
    assert.throws(() => get_serialized_rule_key(rule), /Unknown rule type/);
  });
});

describe("get_parent_stack_id", () => {
  const s = (str: string): string => JSON.stringify(str);
  const mock_colorize = (text: string | number, color: string): string =>
    `[${s(color)}]:${text}`;
  const red = s(Color.RED);
  const gray = s(Color.GRAY);

  const create_mock_pointer = (
    stack_id: number,
    path_id: number,
    step_id: number,
    parent: GraphPointer | null = null,
  ): GraphPointer =>
    new GraphPointer(
      new GraphNode(new RuleEnd(), { stackId: stack_id, pathId: path_id, stepId: step_id }),
      parent,
    );

  it("returns an empty string if there are no parents", () => {
    const pointer = create_mock_pointer(1, 1, 1);
    assert.equal(get_parent_stack_id(pointer, mock_colorize), "");
  });

  it("returns a single parent id colored correctly", () => {
    const parent_pointer = create_mock_pointer(1, 1, 1);
    const pointer = create_mock_pointer(2, 2, 2, parent_pointer);
    assert.equal(get_parent_stack_id(pointer, mock_colorize), `[${red}]:1,1,1`);
  });

  it("returns multiple parent ids separated by colored arrows", () => {
    const grandparent_pointer = create_mock_pointer(0, 0, 0);
    const parent_pointer = create_mock_pointer(1, 1, 1, grandparent_pointer);
    const pointer = create_mock_pointer(2, 2, 2, parent_pointer);
    assert.equal(
      get_parent_stack_id(pointer, mock_colorize),
      `[${red}]:1,1,1[${gray}]:<-[${red}]:0,0,0`,
    );
  });

  it("handles deep nesting of pointers", () => {
    const great_grandparent_pointer = create_mock_pointer(0, 0, 0);
    const grandparent_pointer = create_mock_pointer(1, 1, 1, great_grandparent_pointer);
    const parent_pointer = create_mock_pointer(2, 2, 2, grandparent_pointer);
    const pointer = create_mock_pointer(3, 3, 3, parent_pointer);
    assert.equal(
      get_parent_stack_id(pointer, mock_colorize),
      `[${red}]:2,2,2[${gray}]:<-[${red}]:1,1,1[${gray}]:<-[${red}]:0,0,0`,
    );
  });
});
