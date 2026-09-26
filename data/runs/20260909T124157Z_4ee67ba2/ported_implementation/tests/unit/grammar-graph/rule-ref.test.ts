import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';
import type { GraphNode } from '../../../src/grammar-graph/graph-node.ts';

describe('rule ref', () => {
  test('initializes with a given value', () => {
    assert.equal(new RuleRef(123).value, 123);
  });

  test('allows setting and getting nodes', () => {
    const mockNodes = new Set([1 as unknown as GraphNode]);
    const ruleRef = new RuleRef(123);
    ruleRef.nodes = mockNodes;
    assert.deepStrictEqual(ruleRef.nodes, mockNodes);
  });

  test('throws an error if trying to get nodes before setting', () => {
    const ruleRef = new RuleRef(123);
    assert.throws(() => ruleRef.nodes, { message: 'Nodes are not set' });
  });
});
