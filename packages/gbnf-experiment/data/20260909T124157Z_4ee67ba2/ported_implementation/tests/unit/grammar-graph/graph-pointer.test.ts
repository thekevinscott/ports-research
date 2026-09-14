import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type UnresolvedRule,
} from '../../../src/grammar-graph/grammar-graph-types.ts';
import { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import { GraphPointer } from '../../../src/grammar-graph/graph-pointer.ts';

// The reference suite forces branches with mocked type guards; every case below
// selects the same branch through the real guards.
describe('graph pointer', () => {
  test('constructor', () => {
    const node = new GraphNode(new RuleEnd(), { stackId: 1, pathId: 2, stepId: 3 });
    const pointer = new GraphPointer(node);
    assert.equal(pointer.node, node);
    assert.equal(pointer.id, '1,2,3');
    assert.equal(pointer.parent, null);
  });

  test('it raises error if node is undefined', () => {
    assert.throws(() => new GraphPointer(null as never), { message: 'Node is undefined' });
  });

  test('it initializes correctly with node and parent', () => {
    const parentNode = new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 2, stepId: 3 });
    const childNode = new GraphNode(new RuleChar([98]), { stackId: 4, pathId: 5, stepId: 6 });
    const parentPointer = new GraphPointer(parentNode);
    const childPointer = new GraphPointer(childNode, parentPointer);
    assert.equal(childPointer.parent, parentPointer);
    assert.equal(childPointer.id, '1,2,3-4,5,6');
  });

  describe('resolve', () => {
    test('it raises error on unknown rule types', () => {
      const node = new GraphNode({ type: 'UNKNOWN_RULE_TYPE' } as unknown as UnresolvedRule, {
        stackId: 1,
        pathId: 2,
        stepId: 3,
      });
      const pointer = new GraphPointer(node);
      assert.throws(() => [...pointer.resolve()], /Unknown rule/);
    });

    test('it yields a char rule', () => {
      const node = new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 2, stepId: 3 });
      const pointer = new GraphPointer(node);
      assert.deepStrictEqual([...pointer.resolve()], [pointer]);
    });

    test('it yields a char excluded rule', () => {
      const node = new GraphNode(new RuleCharExclude([97]), {
        stackId: 1,
        pathId: 2,
        stepId: 3,
      });
      const pointer = new GraphPointer(node);
      assert.deepStrictEqual([...pointer.resolve()], [pointer]);
    });

    test('it yields an end rule without a parent', () => {
      const node = new GraphNode(new RuleEnd(), { stackId: 1, pathId: 2, stepId: 3 });
      const pointer = new GraphPointer(node);
      assert.deepStrictEqual([...pointer.resolve()], [pointer]);
    });

    test('it yields an end rule with a parent', () => {
      const rule = new RuleEnd();
      const parentPointer = new GraphPointer(
        new GraphNode(rule, { stackId: 2, pathId: 1, stepId: 1 }),
      );
      const childPointer = new GraphPointer(
        new GraphNode(rule, { stackId: 1, pathId: 1, stepId: 1 }),
        parentPointer,
      );
      assert.deepStrictEqual([...childPointer.resolve()], [parentPointer]);
    });

    test('it yields an end rule with a grandparent', () => {
      const rule = new RuleEnd();
      const grandparentPointer = new GraphPointer(
        new GraphNode(rule, { stackId: 2, pathId: 1, stepId: 1 }),
      );
      const parentPointer = new GraphPointer(
        new GraphNode(rule, { stackId: 2, pathId: 1, stepId: 1 }),
        grandparentPointer,
      );
      const childPointer = new GraphPointer(
        new GraphNode(rule, { stackId: 1, pathId: 1, stepId: 1 }),
        parentPointer,
      );
      assert.deepStrictEqual([...childPointer.resolve()], [grandparentPointer]);
    });

    test('it yields an end rule with a parent that is not an end with a grandparent', () => {
      const rule = new RuleEnd();
      const grandparentPointer = new GraphPointer(
        new GraphNode(rule, { stackId: 2, pathId: 1, stepId: 1 }),
      );
      const parentPointer = new GraphPointer(
        new GraphNode(new RuleChar([97]), { stackId: 2, pathId: 1, stepId: 1 }),
        grandparentPointer,
      );
      const childPointer = new GraphPointer(
        new GraphNode(rule, { stackId: 1, pathId: 1, stepId: 1 }),
        parentPointer,
      );
      assert.deepStrictEqual([...childPointer.resolve()], [parentPointer]);
    });
  });
});
