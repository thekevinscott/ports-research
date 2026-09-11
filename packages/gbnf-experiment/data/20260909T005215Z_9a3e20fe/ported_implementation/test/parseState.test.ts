import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { RuleChar } from '../src/grammarGraph/grammarGraphTypes.ts';
import type { Graph } from '../src/grammarGraph/graph.ts';
import { GraphNode } from '../src/grammarGraph/graphNode.ts';
import { GraphPointer } from '../src/grammarGraph/graphPointer.ts';
import { ParseState } from '../src/grammarGraph/parseState.ts';
import { Pointers } from '../src/grammarGraph/pointers.ts';

interface AddCall {
  input: string;
  pointers: Pointers;
}

/** A Graph stand-in that records `add` calls and echoes back the pointers it was given. */
const makeMockGraph = (): { graph: Graph; calls: AddCall[]; result: Pointers | null } => {
  const state = {
    calls: [] as AddCall[],
    result: null as Pointers | null,
  };
  const graph = {
    grammar: 'sample-grammar',
    add(input: string, pointers: Pointers): Pointers {
      state.calls.push({ input, pointers });
      return state.result ?? pointers;
    },
  };
  return { graph: graph as unknown as Graph, ...state };
};

const makeMockPointers = (): Pointers =>
  new Pointers(
    new GraphPointer(
      new GraphNode(new RuleChar([65]), { stackId: 1, pathId: 1, stepId: 1 }),
    ),
  );

describe('ParseState', () => {
  it('constructs with the given graph and pointers', () => {
    const { graph } = makeMockGraph();
    const parseState = new ParseState(graph, makeMockPointers());
    assert.ok(parseState instanceof ParseState);
  });

  it('returns unique rules from the pointers', () => {
    const { graph } = makeMockGraph();
    const parseState = new ParseState(graph, makeMockPointers());
    const rules = [...parseState.rules()];
    assert.equal(rules.length, 1);
    assert.ok(rules[0] instanceof RuleChar);
    assert.deepStrictEqual(rules[0].value, [65]);
  });

  it('deduplicates rules that serialize identically', () => {
    const { graph } = makeMockGraph();
    const pointers = new Pointers(
      new GraphPointer(new GraphNode(new RuleChar([65]), { stackId: 1, pathId: 1, stepId: 1 })),
      new GraphPointer(new GraphNode(new RuleChar([65]), { stackId: 2, pathId: 2, stepId: 2 })),
      new GraphPointer(new GraphNode(new RuleChar([66]), { stackId: 3, pathId: 3, stepId: 3 })),
    );
    const parseState = new ParseState(graph, pointers);
    assert.equal(parseState.size, 2);
  });

  it('iterates over unique rules using the iterator protocol', () => {
    const { graph } = makeMockGraph();
    const parseState = new ParseState(graph, makeMockPointers());
    const rules = [...parseState];
    assert.equal(rules.length, 1);
    assert.ok(rules[0] instanceof RuleChar);
  });

  it('adds new input and returns a new ParseState with updated pointers', () => {
    const mock = makeMockGraph();
    const mockPointers = makeMockPointers();
    const parseState = new ParseState(mock.graph, mockPointers);
    const newState = parseState.add('B');
    assert.ok(newState instanceof ParseState);
    assert.deepStrictEqual(mock.calls, [{ input: 'B', pointers: mockPointers }]);
  });

  it('rejects non-string input', () => {
    const { graph } = makeMockGraph();
    const parseState = new ParseState(graph, makeMockPointers());
    assert.throws(
      () => parseState.add(66 as unknown as string),
      /input text must be of type string/u,
    );
  });

  it('calculates the size of unique rules correctly', () => {
    const { graph } = makeMockGraph();
    const parseState = new ParseState(graph, makeMockPointers());
    assert.equal(parseState.size, 1);
  });

  it('provides access to the underlying graph grammar', () => {
    const { graph } = makeMockGraph();
    const parseState = new ParseState(graph, makeMockPointers());
    assert.equal(parseState.grammar, 'sample-grammar');
  });
});
