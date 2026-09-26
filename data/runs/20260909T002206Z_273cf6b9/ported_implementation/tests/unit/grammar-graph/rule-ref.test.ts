import { describe, expect, test } from 'vitest';
import type { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';

describe('rule_ref', () => {
  test('initializes with a given value', () => {
    const ruleRef = new RuleRef(123);
    expect(ruleRef.value).toBe(123);
  });

  test('allows setting and getting nodes', () => {
    const mockNodes = new Set([1]) as unknown as Set<GraphNode>;
    const ruleRef = new RuleRef(123);
    ruleRef.nodes = mockNodes;
    expect(ruleRef.nodes).toBe(mockNodes);
  });

  test('throws an error if trying to get nodes before setting', () => {
    const ruleRef = new RuleRef(123);
    expect(() => ruleRef.nodes).toThrow('Nodes are not set');
  });
});
