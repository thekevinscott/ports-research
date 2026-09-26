import { describe, expect, test, vi } from 'vitest';
import { RuleChar } from '../../../src/grammar-graph/grammar-graph-types.ts';
import type { Graph } from '../../../src/grammar-graph/graph.ts';
import { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import { GraphPointer } from '../../../src/grammar-graph/graph-pointer.ts';
import { ParseState } from '../../../src/grammar-graph/parse-state.ts';
import type { Pointers } from '../../../src/grammar-graph/pointers.ts';

const makeMockGraph = () => {
  const graph = {
    add: vi.fn((_input: string, pointers: Pointers) => pointers),
    grammar: 'sample-grammar',
  };
  return graph as unknown as Graph & { add: ReturnType<typeof vi.fn> };
};

const mockPointers = new Set([
  new GraphPointer(
    new GraphNode(new RuleChar([65]), { stackId: 1, pathId: 1, stepId: 1 }),
  ),
]) as unknown as Pointers;

describe('parse_state', () => {
  test('constructs with given graph and pointers', () => {
    const parseState = new ParseState(makeMockGraph(), mockPointers);
    expect(parseState).toBeInstanceOf(ParseState);
  });

  test('returns unique rules from pointers', () => {
    const parseState = new ParseState(makeMockGraph(), mockPointers);
    const rules = [...parseState.rules()];
    expect(rules).toHaveLength(1);
    expect(rules[0]).toBeInstanceOf(RuleChar);
    expect((rules[0] as RuleChar).value).toStrictEqual([65]);
  });

  test('iterates over unique rules using the iterator protocol', () => {
    const parseState = new ParseState(makeMockGraph(), mockPointers);
    const rules = [...parseState];
    expect(rules).toHaveLength(1);
    expect(rules[0]).toBeInstanceOf(RuleChar);
  });

  test('adds new input and returns new parse state with updated pointers', () => {
    const mockGraph = makeMockGraph();
    const parseState = new ParseState(mockGraph, mockPointers);
    const newState = parseState.add('B');
    expect(newState).toBeInstanceOf(ParseState);
    expect(mockGraph.add).toHaveBeenCalledWith('B', mockPointers);
  });

  test('calculates the size of unique rules correctly', () => {
    const parseState = new ParseState(makeMockGraph(), mockPointers);
    expect(parseState.size).toBe(1);
  });

  test('provides access to the underlying graph grammar', () => {
    const parseState = new ParseState(makeMockGraph(), mockPointers);
    expect(parseState.grammar).toBe('sample-grammar');
  });
});
