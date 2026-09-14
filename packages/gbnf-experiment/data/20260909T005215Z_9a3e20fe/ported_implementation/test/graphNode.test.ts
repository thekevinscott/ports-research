import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import type { GraphNodeMeta } from '../src/grammarGraph/graphNode.ts';
import { GraphNode } from '../src/grammarGraph/graphNode.ts';
import { printGraphNode } from '../src/grammarGraph/print.ts';
import { RuleRef } from '../src/grammarGraph/ruleRef.ts';

describe('GraphNode', () => {
  const meta: GraphNodeMeta = { stackId: 1, pathId: 2, stepId: 3 };
  const rule = new RuleRef(42);

  it('constructs with a rule and meta', () => {
    const node = new GraphNode(rule, meta);
    assert.equal(node.rule, rule);
    assert.equal(node.meta, meta);
  });

  it('throws if meta is undefined', () => {
    assert.throws(() => new GraphNode(rule, null), /Meta is undefined/u);
  });

  it('correctly calculates and caches its id', () => {
    const node = new GraphNode(rule, meta);
    assert.equal(node.id, '1,2,3');
    node.meta = { stackId: 4, pathId: 5, stepId: 6 };
    assert.equal(node.id, '1,2,3');
  });

  it('delegates print to the printGraphNode function', () => {
    const node = new GraphNode(rule, meta);
    const opts = { colorize: (x: string | number): string => String(x), showPosition: false };
    assert.equal(node.print(opts), printGraphNode(node)(opts));
  });

  it('handles next node linkage', () => {
    const nextNode = new GraphNode(new RuleRef(43), meta);
    const node = new GraphNode(rule, meta, nextNode);
    assert.equal(node.next, nextNode);
  });
});
