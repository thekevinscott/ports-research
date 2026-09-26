import { beforeEach, describe, expect, test, vi } from 'vitest';
import type { PrintOpts } from '../../../src/grammar-graph/grammar-graph-types.ts';
import { GraphNode, type GraphNodeMeta } from '../../../src/grammar-graph/graph-node.ts';
import { printGraphNode } from '../../../src/grammar-graph/print.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';

vi.mock('../../../src/grammar-graph/print.ts', () => ({
  printGraphNode: vi.fn(() => () => 'mocked_response'),
  printGraphPointer: vi.fn(() => () => 'mocked_response'),
}));

const meta: GraphNodeMeta = { stackId: 1, pathId: 2, stepId: 3 };
const rule = new RuleRef(42);

beforeEach(() => {
  vi.mocked(printGraphNode).mockClear();
});

describe('graph_node', () => {
  test('construct with rule and meta', () => {
    const node = new GraphNode(rule, meta);
    expect(node.rule).toBe(rule);
    expect(node.meta).toBe(meta);
  });

  test('throw if meta is undefined', () => {
    expect(() => new GraphNode(rule, null)).toThrow('Meta is undefined');
  });

  test('correctly calculate and cache its id', () => {
    const node = new GraphNode(rule, meta);
    expect(node.id).toBe('1,2,3');
    node.meta = { stackId: 4, pathId: 5, stepId: 6 };
    expect(node.id).toBe('1,2,3');
  });

  test('delegate print to the print_graph_node function', () => {
    const node = new GraphNode(rule, meta);
    const opts: PrintOpts = { colorize: x => String(x), show_position: false };
    expect(node.print(opts)).toBe('mocked_response');
    expect(printGraphNode).toHaveBeenCalledWith(node);
  });

  test('handle next node linkage', () => {
    const nextNode = new GraphNode(new RuleRef(43), meta);
    const node = new GraphNode(rule, meta, nextNode);
    expect(node.next).toBe(nextNode);
  });
});
