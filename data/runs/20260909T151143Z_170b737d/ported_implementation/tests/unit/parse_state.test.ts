import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { RuleChar } from "../../src/grammar_graph/grammar_graph_types.ts";
import type { Graph } from "../../src/grammar_graph/graph.ts";
import { GraphNode } from "../../src/grammar_graph/graph_node.ts";
import { GraphPointer } from "../../src/grammar_graph/graph_pointer.ts";
import { ParseState } from "../../src/grammar_graph/parse_state.ts";
import { Pointers } from "../../src/grammar_graph/pointers.ts";

const meta = { stackId: 1, pathId: 1, stepId: 1 };

class MockGraph {
  grammar = "sample-grammar";
  calls: Array<[string, Pointers]> = [];
  next_pointers: Pointers | null = null;

  add(input: string, pointers: Pointers): Pointers {
    this.calls.push([input, pointers]);
    return this.next_pointers ?? pointers;
  }
}

const make_mock_graph = (): MockGraph => new MockGraph();
const as_graph = (graph: MockGraph): Graph => graph as unknown as Graph;

const make_mock_pointers = (): Pointers =>
  new Pointers(new GraphPointer(new GraphNode(new RuleChar([65]), meta)));

describe("ParseState", () => {
  it("constructs with the given graph and pointers", () => {
    const parse_state = new ParseState(as_graph(make_mock_graph()), make_mock_pointers());
    assert.ok(parse_state instanceof ParseState);
  });

  it("returns unique rules from pointers", () => {
    const parse_state = new ParseState(as_graph(make_mock_graph()), make_mock_pointers());
    const rules = [...parse_state.rules()];
    assert.equal(rules.length, 1);
    assert.ok(rules[0] instanceof RuleChar);
    assert.deepStrictEqual((rules[0] as RuleChar).value, [65]);
  });

  it("de-duplicates equal rules held by different pointers", () => {
    const pointers = new Pointers(
      new GraphPointer(new GraphNode(new RuleChar([65]), meta)),
      new GraphPointer(new GraphNode(new RuleChar([65]), { stackId: 2, pathId: 2, stepId: 2 })),
    );
    const parse_state = new ParseState(as_graph(make_mock_graph()), pointers);
    assert.equal(parse_state.size, 1);
  });

  it("iterates over unique rules", () => {
    const parse_state = new ParseState(as_graph(make_mock_graph()), make_mock_pointers());
    const rules = [...parse_state];
    assert.equal(rules.length, 1);
    assert.ok(rules[0] instanceof RuleChar);
  });

  it("adds new input and returns a new parse state with updated pointers", () => {
    const mock_graph = make_mock_graph();
    const new_pointers = new Pointers(
      new GraphPointer(new GraphNode(new RuleChar([66]), meta)),
    );
    mock_graph.next_pointers = new_pointers;
    const mock_pointers = make_mock_pointers();

    const parse_state = new ParseState(as_graph(mock_graph), mock_pointers);
    const new_state = parse_state.add("B");

    assert.ok(new_state instanceof ParseState);
    assert.deepStrictEqual(mock_graph.calls, [["B", mock_pointers]]);
    assert.deepStrictEqual(
      [...new_state].map((rule) => (rule as RuleChar).value),
      [[66]],
    );
  });

  it("rejects non-string input", () => {
    const parse_state = new ParseState(as_graph(make_mock_graph()), make_mock_pointers());
    assert.throws(
      () => parse_state.add(1 as unknown as string),
      /input text must be of type string/,
    );
  });

  it("calculates the size of unique rules", () => {
    const parse_state = new ParseState(as_graph(make_mock_graph()), make_mock_pointers());
    assert.equal(parse_state.size, 1);
  });

  it("provides access to the underlying graph grammar", () => {
    const parse_state = new ParseState(as_graph(make_mock_graph()), make_mock_pointers());
    assert.equal(parse_state.grammar, "sample-grammar");
  });
});
