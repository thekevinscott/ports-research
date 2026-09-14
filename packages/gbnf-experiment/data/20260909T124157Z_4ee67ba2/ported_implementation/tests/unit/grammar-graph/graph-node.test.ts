import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import type { PrintOpts } from '../../../src/grammar-graph/grammar-graph-types.ts';
import { GraphNode, type GraphNodeMeta } from '../../../src/grammar-graph/graph-node.ts';
import { printGraphNode } from '../../../src/grammar-graph/print.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';

const meta: GraphNodeMeta = { stackId: 1, pathId: 2, stepId: 3 };
const rule = new RuleRef(42);

describe('graph node', () => {
  test('construct with rule and meta', () => {
    const node = new GraphNode(rule, meta);
    assert.equal(node.rule, rule);
    assert.equal(node.meta, meta);
  });

  test('throw if meta is undefined', () => {
    assert.throws(() => new GraphNode(rule, null), { message: 'Meta is undefined' });
  });

  test('correctly calculate and cache its id', () => {
    const node = new GraphNode(rule, meta);
    assert.equal(node.id, '1,2,3');
    node.meta = { stackId: 4, pathId: 5, stepId: 6 };
    assert.equal(node.id, '1,2,3');
  });

  // The reference test patches print_graph_node to assert delegation; here the
  // delegation is asserted by comparing against the real printer's output.
  test('delegate print to the print graph node function', () => {
    const node = new GraphNode(rule, meta);
    const opts: PrintOpts = { colorize: x => String(x), show_position: false };
    assert.equal(node.print(opts), printGraphNode(node)(opts));
  });

  test('handle next node linkage', () => {
    const nextNode = new GraphNode(new RuleRef(43), meta);
    const node = new GraphNode(rule, meta, nextNode);
    assert.equal(node.next, nextNode);
  });
});
