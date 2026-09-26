import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { RuleChar } from '../../../src/grammar-graph/grammar-graph-types.ts';
import type { Graph } from '../../../src/grammar-graph/graph.ts';
import { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import { GraphPointer } from '../../../src/grammar-graph/graph-pointer.ts';
import { ParseState } from '../../../src/grammar-graph/parse-state.ts';
import { Pointers } from '../../../src/grammar-graph/pointers.ts';

interface MockGraph extends Graph {
  calls: [string, Pointers][];
}

const makeMockGraph = (): MockGraph => {
  const calls: [string, Pointers][] = [];
  return {
    calls,
    grammar: 'sample-grammar',
    add(input: string, pointers: Pointers) {
      calls.push([input, pointers]);
      return pointers;
    },
  } as unknown as MockGraph;
};

const makeMockPointers = (): Pointers =>
  new Pointers(
    new GraphPointer(new GraphNode(new RuleChar([65]), { stackId: 1, pathId: 1, stepId: 1 })),
  );

describe('parse state', () => {
  test('constructs with given graph and pointers', () => {
    assert.ok(new ParseState(makeMockGraph(), makeMockPointers()) instanceof ParseState);
  });

  test('returns unique rules from pointers', () => {
    const rules = [...new ParseState(makeMockGraph(), makeMockPointers()).rules()];
    assert.equal(rules.length, 1);
    assert.ok(rules[0] instanceof RuleChar);
    assert.deepStrictEqual(rules[0].value, [65]);
  });

  test('iterates over unique rules using the iterator protocol', () => {
    const rules = [...new ParseState(makeMockGraph(), makeMockPointers())];
    assert.equal(rules.length, 1);
    assert.ok(rules[0] instanceof RuleChar);
  });

  test('adds new input and returns new parse state with updated pointers', () => {
    const mockGraph = makeMockGraph();
    const mockPointers = makeMockPointers();
    const parseState = new ParseState(mockGraph, mockPointers);
    const newState = parseState.add('B');
    assert.ok(newState instanceof ParseState);
    assert.deepStrictEqual(mockGraph.calls, [['B', mockPointers]]);
  });

  test('rejects non-string input', () => {
    const parseState = new ParseState(makeMockGraph(), makeMockPointers());
    assert.throws(() => parseState.add(1 as never), {
      message: 'input text must be of type string',
    });
  });

  test('calculates the size of unique rules correctly', () => {
    assert.equal(new ParseState(makeMockGraph(), makeMockPointers()).size, 1);
  });

  test('provides access to the underlying graph grammar', () => {
    assert.equal(new ParseState(makeMockGraph(), makeMockPointers()).grammar, 'sample-grammar');
  });
});
