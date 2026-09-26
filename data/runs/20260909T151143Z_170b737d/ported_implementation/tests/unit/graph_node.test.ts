import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { RuleChar, RuleEnd } from "../../src/grammar_graph/grammar_graph_types.ts";
import { GraphNode, type GraphNodeMeta } from "../../src/grammar_graph/graph_node.ts";
import { Pointers } from "../../src/grammar_graph/pointers.ts";
import { RuleRef } from "../../src/grammar_graph/rule_ref.ts";

const meta: GraphNodeMeta = { stackId: 1, pathId: 2, stepId: 3 };

describe("GraphNode", () => {
  it("constructs with a rule and meta", () => {
    const rule = new RuleRef(42);
    const node = new GraphNode(rule, meta);
    assert.equal(node.rule, rule);
    assert.deepStrictEqual(node.meta, meta);
    assert.equal(node.next, null);
  });

  it("throws if meta is undefined", () => {
    assert.throws(() => new GraphNode(new RuleRef(42), null), /Meta is undefined/);
  });

  it("calculates and caches its id", () => {
    const node = new GraphNode(new RuleRef(42), { ...meta });
    assert.equal(node.id, "1,2,3");
    node.meta = { stackId: 4, pathId: 5, stepId: 6 };
    assert.equal(node.id, "1,2,3");
  });

  it("handles next node linkage", () => {
    const nextNode = new GraphNode(new RuleRef(43), meta);
    const node = new GraphNode(new RuleRef(42), meta, nextNode);
    assert.equal(node.next, nextNode);
  });

  it("delegates print to print_graph_node", () => {
    const node = new GraphNode(new RuleChar([65]), meta);
    assert.equal(
      node.print({ colorize: (x) => String(x), show_position: false, pointers: new Pointers() }),
      "[A]",
    );
  });

  it("propagates the reference's AttributeError for rules without a `type`", () => {
    const node = new GraphNode(new RuleEnd(), meta);
    assert.throws(
      () => node.print({ colorize: (x) => String(x) }),
      /'RuleEnd' object has no attribute 'type'/,
    );
  });
});
