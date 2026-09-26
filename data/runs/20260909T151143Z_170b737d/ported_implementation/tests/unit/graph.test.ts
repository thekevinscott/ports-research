import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { Graph } from "../../src/grammar_graph/graph.ts";
import { GraphNode } from "../../src/grammar_graph/graph_node.ts";
import { GraphPointer } from "../../src/grammar_graph/graph_pointer.ts";
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type UnresolvedRule,
} from "../../src/grammar_graph/grammar_graph_types.ts";
import { Pointers } from "../../src/grammar_graph/pointers.ts";
import { RuleRef } from "../../src/grammar_graph/rule_ref.ts";

const grammar = "example-grammar";
const stackedRules: UnresolvedRule[][][] = [
  [[new RuleChar([65, 66, 67])], [new RuleChar([68, 69, 70])]],
  [[new RuleChar([71, 72, 73])], [new RuleChar([74, 75, 76])]],
];
const root_id = 0;
const meta = { stackId: 1, pathId: 1, stepId: 1 };

describe("Graph", () => {
  it("creates a graph instance", () => {
    const graph = new Graph(grammar, stackedRules, root_id);
    assert.ok(graph instanceof Graph);
    assert.equal(graph.grammar, grammar);
  });

  it("gets the root node", () => {
    const graph = new Graph(grammar, stackedRules, root_id);
    const root_node = graph.__get_root_node__(root_id);
    assert.ok(root_node instanceof Map);
    assert.equal(root_node.size, 2);
  });

  it("throws for an unknown root node", () => {
    const graph = new Graph(grammar, stackedRules, root_id);
    assert.throws(() => graph.__get_root_node__(99), /Root node not found for value: 99/);
  });

  it("prints the graph", () => {
    const graph = new Graph(grammar, stackedRules, root_id);
    assert.equal(
      graph.print(),
      "{0,0,0}[ABC]\n{0,1,0}[DEF]\n{1,0,0}[GHI]\n{1,1,0}[JKL]",
    );

    const printed_with_colors = graph.print(null, true);
    assert.ok(printed_with_colors.length > 0);
    assert.ok(printed_with_colors.startsWith("\x1b[34m{\x1b[90m0,0,0"));
  });

  it("iterates over pointers, grouping by rule", () => {
    const graph = new Graph(grammar, stackedRules, root_id);
    const mock_pointers = [
      new RuleChar([65, 66, 67]),
      new RuleChar([68, 69, 70]),
      new RuleChar([71, 72, 73]),
      new RuleChar([74, 75, 76]),
      new RuleCharExclude([1]),
      new RuleEnd(),
    ].map((rule) => new GraphPointer(new GraphNode(rule, meta)));

    const result = [...graph.__iterate_over_pointers__(mock_pointers)];
    assert.equal(result.length, 6);
    for (const [rule, pointers] of result) {
      assert.ok(rule !== undefined);
      // The reference seeds each group with its first pointer and then appends
      // it again, so a single-pointer group holds two entries.
      assert.equal(pointers.length, 2);
    }
  });

  it("raises when a reference rule reaches the pointer iteration", () => {
    const graph = new Graph(grammar, stackedRules, root_id);
    const mock_pointers = [new GraphPointer(new GraphNode(new RuleRef(0), meta))];
    assert.throws(
      () => [...graph.__iterate_over_pointers__(mock_pointers)],
      /Encountered a reference rule in the graph/,
    );
  });

  it("resolves references into the referenced nodes", () => {
    const ref = new RuleRef(1);
    const graph = new Graph(
      grammar,
      [
        [[ref, new RuleEnd()]],
        [[new RuleChar([97]), new RuleEnd()], [new RuleChar([98]), new RuleEnd()]],
      ],
      0,
    );
    assert.equal(graph.__roots__.size, 2);
    assert.deepStrictEqual(
      [...ref.nodes].map((node) => node.id),
      ["1,0,0", "1,1,0"],
    );
  });

  it("walks input and reports the parse error position", () => {
    const graph = new Graph(
      grammar,
      [[[new RuleChar([102]), new RuleChar([111]), new RuleEnd()]]],
      0,
    );
    const pointers = graph.add("f");
    assert.ok(pointers instanceof Pointers);
    assert.equal(pointers.length, 1);
    assert.throws(() => graph.add("x", pointers), /Failed to parse input string/);
  });

  it("rejects an unsupported rule while parsing", () => {
    const graph = new Graph(grammar, stackedRules, root_id);
    const pointers = new Pointers(
      new GraphPointer(
        new GraphNode({ value: "UNKNOWN" } as unknown as UnresolvedRule, meta),
      ),
    );
    assert.throws(() => graph.__parse__(pointers, 65), /Unsupported rule/);
  });

  it("rejects non-string input", () => {
    const graph = new Graph(grammar, stackedRules, root_id);
    assert.throws(
      () => graph.add(97 as unknown as string),
      /src must be a string in graph\.add/,
    );
  });
});

describe("Pointers", () => {
  it("de-duplicates by pointer id", () => {
    const node = new GraphNode(new RuleChar([97]), meta);
    const pointers = new Pointers(new GraphPointer(node), new GraphPointer(node));
    assert.equal(pointers.length, 1);
  });

  it("is iterable in insertion order", () => {
    const first = new GraphPointer(new GraphNode(new RuleChar([97]), meta));
    const second = new GraphPointer(
      new GraphNode(new RuleChar([98]), { stackId: 2, pathId: 2, stepId: 2 }),
    );
    const pointers = new Pointers(first, second);
    assert.deepStrictEqual([...pointers], [first, second]);
  });
});
