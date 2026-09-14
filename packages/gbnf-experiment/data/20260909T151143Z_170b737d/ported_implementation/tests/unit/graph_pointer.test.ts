import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type UnresolvedRule,
} from "../../src/grammar_graph/grammar_graph_types.ts";
import { GraphNode } from "../../src/grammar_graph/graph_node.ts";
import { GraphPointer } from "../../src/grammar_graph/graph_pointer.ts";
import { RuleRef } from "../../src/grammar_graph/rule_ref.ts";

const meta = { stackId: 1, pathId: 2, stepId: 3 };

describe("GraphPointer", () => {
  it("initializes from a node", () => {
    const node = new GraphNode(new RuleEnd(), meta);
    const pointer = new GraphPointer(node);
    assert.equal(pointer.node, node);
    assert.equal(pointer.id, "1,2,3");
    assert.equal(pointer.parent, null);
    assert.equal(pointer.rule, node.rule);
    assert.equal(pointer.valid, null);
  });

  it("raises if the node is undefined", () => {
    assert.throws(
      () => new GraphPointer(undefined as unknown as GraphNode),
      /Node is undefined/,
    );
  });

  it("initializes correctly with a node and a parent", () => {
    const parent_node = new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 2, stepId: 3 });
    const child_node = new GraphNode(new RuleChar([98]), { stackId: 4, pathId: 5, stepId: 6 });
    const parent_pointer = new GraphPointer(parent_node);
    const child_pointer = new GraphPointer(child_node, parent_pointer);
    assert.equal(child_pointer.parent, parent_pointer);
    assert.equal(child_pointer.id, "1,2,3-4,5,6");
  });

  describe("resolve", () => {
    it("raises on unknown rule types", () => {
      const node = new GraphNode(
        { type: "UNKNOWN_RULE_TYPE" } as unknown as UnresolvedRule,
        meta,
      );
      const pointer = new GraphPointer(node);
      assert.throws(() => [...pointer.resolve()], /Unknown rule/);
    });

    it("yields a char rule", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleChar([97]), meta));
      assert.deepStrictEqual([...pointer.resolve()], [pointer]);
    });

    it("yields a char-excluded rule", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleCharExclude([97]), meta));
      assert.deepStrictEqual([...pointer.resolve()], [pointer]);
    });

    it("yields an end rule without a parent", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleEnd(), meta));
      assert.deepStrictEqual([...pointer.resolve()], [pointer]);
    });

    it("delegates to the parent for an end rule with a parent", () => {
      // The parent is a ref rule whose `next` is a char rule, so resolving the
      // end rule walks up to the parent and continues from its next node.
      const char_node = new GraphNode(new RuleChar([97]), { stackId: 2, pathId: 0, stepId: 1 });
      const ref_node = new GraphNode(
        new RuleRef(9),
        { stackId: 2, pathId: 0, stepId: 0 },
        char_node,
      );
      const parent_pointer = new GraphPointer(ref_node);
      const child_pointer = new GraphPointer(
        new GraphNode(new RuleEnd(), { stackId: 1, pathId: 1, stepId: 1 }),
        parent_pointer,
      );

      const resolved = [...child_pointer.resolve()];
      assert.equal(resolved.length, 1);
      assert.equal(resolved[0].node, char_node);
      assert.equal(resolved[0].parent, null);
    });

    it("expands a ref rule into its referenced nodes", () => {
      const first = new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 0, stepId: 0 });
      const second = new GraphNode(new RuleChar([98]), { stackId: 1, pathId: 1, stepId: 0 });
      const rule_ref = new RuleRef(1);
      rule_ref.nodes = new Set([first, second]);
      const pointer = new GraphPointer(new GraphNode(rule_ref, meta));

      const resolved = [...pointer.resolve()];
      assert.deepStrictEqual(
        resolved.map((p) => p.node),
        [first, second],
      );
      assert.deepStrictEqual(
        resolved.map((p) => p.id),
        ["1,2,3-1,0,0", "1,2,3-1,1,0"],
      );
    });
  });

  describe("fetch_next", () => {
    it("yields nothing when the pointer is not valid", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleChar([97]), meta));
      assert.deepStrictEqual([...pointer.fetch_next()], []);
    });

    it("yields the resolved next node when valid", () => {
      const next_node = new GraphNode(new RuleChar([98]), { stackId: 1, pathId: 2, stepId: 4 });
      const pointer = new GraphPointer(new GraphNode(new RuleChar([97]), meta, next_node));
      pointer.valid = true;
      const next = [...pointer.fetch_next()];
      assert.deepStrictEqual(
        next.map((p) => p.node),
        [next_node],
      );
    });

    it("yields nothing for a valid end rule without a parent", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleEnd(), meta));
      pointer.valid = true;
      assert.deepStrictEqual([...pointer.fetch_next()], []);
    });

    it("throws when a non-end node has no next", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleChar([97]), meta));
      pointer.valid = true;
      assert.throws(() => [...pointer.fetch_next()], /No next node/);
    });
  });
});
