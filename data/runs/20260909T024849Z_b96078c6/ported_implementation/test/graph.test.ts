import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from "../src/grammar-graph/grammar-graph-types.ts";
import type { UnresolvedRule } from "../src/grammar-graph/grammar-graph-types.ts";
import { Graph } from "../src/grammar-graph/graph.ts";
import { GraphNode } from "../src/grammar-graph/graph-node.ts";
import { GraphPointer } from "../src/grammar-graph/graph-pointer.ts";
import { ParseState } from "../src/grammar-graph/parse-state.ts";
import { Pointers } from "../src/grammar-graph/pointers.ts";
import { RuleRef } from "../src/grammar-graph/rule-ref.ts";

const GRAMMAR = "example-grammar";

const stackedRules: UnresolvedRule[][][] = [
  [
    [new RuleChar([65, 66, 67]), new RuleEnd()],
    [new RuleChar([68, 69, 70]), new RuleEnd()],
  ],
  [
    [new RuleChar([71, 72, 73]), new RuleEnd()],
    [new RuleChar([74, 75, 76]), new RuleEnd()],
  ],
];

const makeGraph = () => new Graph(GRAMMAR, stackedRules, 0);

describe("Graph", () => {
  it("creates a graph instance", () => {
    const graph = makeGraph();
    assert.ok(graph instanceof Graph);
    assert.equal(graph.grammar, GRAMMAR);
  });

  it("gets the root node", () => {
    const rootNode = makeGraph().getRootNode(0);
    assert.ok(rootNode instanceof Map);
    assert.equal(rootNode.size, 2);
  });

  it("throws when a root node does not exist", () => {
    assert.throws(() => makeGraph().getRootNode(42), {
      message: "Root node not found for value: 42",
    });
  });

  it("throws when the root id has no stack", () => {
    assert.throws(() => new Graph(GRAMMAR, stackedRules, 42), {
      message: "Root node not found for value: 42",
    });
  });

  it("gets the initial pointers", () => {
    const pointers = makeGraph().getInitialPointers();
    assert.ok(pointers instanceof Pointers);
    assert.equal(pointers.size, 2);
  });

  it("resolves rule refs to the referenced nodes", () => {
    const ruleRef = new RuleRef(1);
    const graph = new Graph(
      GRAMMAR,
      [[[ruleRef, new RuleEnd()]], stackedRules[1]],
      0,
    );
    assert.equal(ruleRef.nodes.size, 2);
    assert.equal(graph.getInitialPointers().size, 2);
  });

  it("prints the graph", () => {
    const printed = makeGraph().print(null, true);
    assert.ok(typeof printed === "string");
    assert.ok(printed.length > 0);
    assert.equal(printed.split("\n").length, 4);
  });

  it("prints the graph without colors", () => {
    assert.deepEqual(makeGraph().print().split("\n"), [
      "{0,0,0}[ABC]-> {0,0,1}RuleEnd",
      "{0,1,0}[DEF]-> {0,1,1}RuleEnd",
      "{1,0,0}[GHI]-> {1,0,1}RuleEnd",
      "{1,1,0}[JKL]-> {1,1,1}RuleEnd",
    ]);
  });

  it("iterates over pointers, grouped by rule", () => {
    const graph = makeGraph();
    const meta = { stackId: 0, pathId: 0, stepId: 0 };
    const pointers = new Pointers(
      new GraphPointer(new GraphNode(new RuleChar([65]), meta)),
      new GraphPointer(
        new GraphNode(new RuleCharExclude([66]), { ...meta, stepId: 1 }),
      ),
      new GraphPointer(new GraphNode(new RuleEnd(), { ...meta, stepId: 2 })),
    );
    const result = [...graph.iterateOverPointers(pointers)];
    assert.equal(result.length, 3);
    for (const [rule, groupedPointers] of result) {
      assert.ok(rule instanceof RuleChar || rule instanceof RuleCharExclude || rule instanceof RuleEnd);
      assert.ok(groupedPointers.length >= 1);
    }
  });

  it("raises an error when iterating over a reference rule", () => {
    const graph = makeGraph();
    const ruleRef = new RuleRef(0);
    const pointers = new Pointers(
      new GraphPointer(
        new GraphNode(ruleRef, { stackId: 0, pathId: 0, stepId: 0 }),
      ),
    );
    assert.throws(() => [...graph.iterateOverPointers(pointers)], {
      message: "Encountered a reference rule in the graph",
    });
  });

  it("rejects non-string input", () => {
    assert.throws(() => makeGraph().add(97 as never), {
      message: "src must be a string in graph.add",
    });
  });

  it("walks the graph as input is added", () => {
    const graph = makeGraph();
    const pointers = graph.add("A");
    assert.equal(pointers.size, 1);
    assert.deepEqual(graph.previousCodePoints, [65]);
  });

  it("throws an InputParseError when no pointers remain", () => {
    assert.throws(() => makeGraph().add("Z"), {
      name: "InputParseError",
    });
  });
});

describe("ParseState", () => {
  const meta = { stackId: 1, pathId: 2, stepId: 3 };
  const mockGraph = () =>
    ({
      grammar: "sample-grammar",
      add: (_text: string, _pointers?: Pointers) => mockPointers(),
    }) as unknown as Graph;
  const mockPointers = () =>
    new Pointers(
      new GraphPointer(new GraphNode(new RuleChar([65]), meta)),
      new GraphPointer(
        new GraphNode(new RuleChar([65]), { stackId: 9, pathId: 9, stepId: 9 }),
      ),
    );

  it("constructs with the given graph and pointers", () => {
    assert.ok(new ParseState(mockGraph(), mockPointers()) instanceof ParseState);
  });

  it("returns unique rules from its pointers", () => {
    const rules = [...new ParseState(mockGraph(), mockPointers()).rules()];
    assert.equal(rules.length, 1);
    assert.ok(rules[0] instanceof RuleChar);
    assert.deepEqual(rules[0].value, [65]);
  });

  it("iterates over unique rules", () => {
    const rules = [...new ParseState(mockGraph(), mockPointers())];
    assert.equal(rules.length, 1);
    assert.ok(rules[0] instanceof RuleChar);
  });

  it("calculates the size of unique rules correctly", () => {
    assert.equal(new ParseState(mockGraph(), mockPointers()).size, 1);
  });

  it("adds new input and returns a new parse state", () => {
    const state = new ParseState(mockGraph(), mockPointers());
    const next = state.add("B");
    assert.ok(next instanceof ParseState);
    assert.notEqual(next, state);
  });

  it("rejects non-string input", () => {
    assert.throws(() => new ParseState(mockGraph(), mockPointers()).add(1 as never), {
      message: "input text must be of type string",
    });
  });

  it("provides access to the underlying graph's grammar", () => {
    assert.equal(new ParseState(mockGraph(), mockPointers()).grammar, "sample-grammar");
  });
});
