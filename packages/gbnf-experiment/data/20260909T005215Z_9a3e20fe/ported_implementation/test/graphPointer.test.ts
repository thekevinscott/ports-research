import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { RuleChar, RuleCharExclude, RuleEnd } from '../src/grammarGraph/grammarGraphTypes.ts';
import type { UnresolvedRule } from '../src/grammarGraph/grammarGraphTypes.ts';
import { GraphNode } from '../src/grammarGraph/graphNode.ts';
import { GraphPointer } from '../src/grammarGraph/graphPointer.ts';

describe('GraphPointer', () => {
  it('constructs from a node', () => {
    const node = new GraphNode(new RuleEnd(), { stackId: 1, pathId: 2, stepId: 3 });
    const pointer = new GraphPointer(node);
    assert.equal(pointer.node, node);
    assert.equal(pointer.id, '1,2,3');
    assert.equal(pointer.parent, null);
  });

  it('throws an error if the node is undefined', () => {
    assert.throws(
      () => new GraphPointer(null as unknown as GraphNode),
      /Node is undefined/u,
    );
  });

  it('initializes correctly with a node and a parent', () => {
    const parentNode = new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 2, stepId: 3 });
    const childNode = new GraphNode(new RuleChar([98]), { stackId: 4, pathId: 5, stepId: 6 });
    const parentPointer = new GraphPointer(parentNode);
    const childPointer = new GraphPointer(childNode, parentPointer);
    assert.equal(childPointer.parent, parentPointer);
    assert.equal(childPointer.id, '1,2,3-4,5,6');
  });

  describe('resolve', () => {
    it('throws an error on unknown rule types', () => {
      const node = new GraphNode({ type: 'UNKNOWN_RULE_TYPE' } as unknown as UnresolvedRule, {
        stackId: 1,
        pathId: 2,
        stepId: 3,
      });
      const pointer = new GraphPointer(node);
      assert.throws(() => [...pointer.resolve()], /Unknown rule/u);
    });

    it('yields a char rule', () => {
      const node = new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 2, stepId: 3 });
      const pointer = new GraphPointer(node);
      assert.deepStrictEqual([...pointer.resolve()], [pointer]);
    });

    it('yields a char excluded rule', () => {
      const node = new GraphNode(new RuleCharExclude([97]), { stackId: 1, pathId: 2, stepId: 3 });
      const pointer = new GraphPointer(node);
      assert.deepStrictEqual([...pointer.resolve()], [pointer]);
    });

    it('yields an end rule without a parent', () => {
      const node = new GraphNode(new RuleEnd(), { stackId: 1, pathId: 2, stepId: 3 });
      const pointer = new GraphPointer(node);
      assert.deepStrictEqual([...pointer.resolve()], [pointer]);
    });

    it('yields an end rule with a parent', () => {
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

    it('yields an end rule with a grandparent', () => {
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

    it('yields an end rule whose parent is not an end, with a grandparent', () => {
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

  describe('fetchNext', () => {
    it('yields nothing when the pointer is not valid', () => {
      const pointer = new GraphPointer(
        new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 1, stepId: 1 }),
      );
      assert.deepStrictEqual([...pointer.fetchNext()], []);
    });

    it('yields the next node when the pointer is valid', () => {
      const next = new GraphNode(new RuleEnd(), { stackId: 1, pathId: 1, stepId: 1 });
      const node = new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 1, stepId: 0 }, next);
      const pointer = new GraphPointer(node);
      pointer.valid = true;
      const [resolved, ...rest] = [...pointer.fetchNext()];
      assert.equal(rest.length, 0);
      assert.equal(resolved.node, next);
    });

    it('throws when a valid non-end pointer has no next node', () => {
      const pointer = new GraphPointer(
        new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 1, stepId: 0 }),
      );
      pointer.valid = true;
      assert.throws(() => [...pointer.fetchNext()], /No next node/u);
    });
  });
});
