import { beforeEach, describe, expect, test, vi } from 'vitest';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from '../../../src/grammar-graph/grammar-graph-types.ts';
import { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import { GraphPointer } from '../../../src/grammar-graph/graph-pointer.ts';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
} from '../../../src/grammar-graph/type-guards.ts';

vi.mock('../../../src/grammar-graph/type-guards.ts', async importOriginal => {
  const actual = await importOriginal<
    typeof import('../../../src/grammar-graph/type-guards.ts')
  >();
  return {
    ...actual,
    isGraphPointerRuleRef: vi.fn(() => false),
    isGraphPointerRuleEnd: vi.fn(() => false),
    isGraphPointerRuleChar: vi.fn(() => false),
    isGraphPointerRuleCharExclude: vi.fn(() => false),
  };
});

const guards = [
  isGraphPointerRuleRef,
  isGraphPointerRuleEnd,
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
];

beforeEach(() => {
  for (const guard of guards) {
    vi.mocked(guard).mockReset();
    vi.mocked(guard).mockReturnValue(false);
  }
});

describe('graph_pointer', () => {
  test('constructor', () => {
    const node = new GraphNode(new RuleEnd(), { stackId: 1, pathId: 2, stepId: 3 });
    const pointer = new GraphPointer(node);
    expect(pointer.node).toBe(node);
    expect(pointer.id).toBe('1,2,3');
    expect(pointer.parent).toBeNull();
  });

  test('it raises error if node is undefined', () => {
    expect(() => new GraphPointer(null as never)).toThrow('Node is undefined');
  });

  test('it initializes correctly with node and parent', () => {
    const parentNode = new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 2, stepId: 3 });
    const childNode = new GraphNode(new RuleChar([98]), { stackId: 4, pathId: 5, stepId: 6 });
    const parentPointer = new GraphPointer(parentNode);
    const childPointer = new GraphPointer(childNode, parentPointer);
    expect(childPointer.parent).toBe(parentPointer);
    expect(childPointer.id).toBe('1,2,3-4,5,6');
  });

  describe('resolve', () => {
    test('it raises error on unknown rule types', () => {
      const node = new GraphNode(
        { type: 'UNKNOWN_RULE_TYPE' } as never,
        { stackId: 1, pathId: 2, stepId: 3 },
      );
      const pointer = new GraphPointer(node);
      expect(() => [...pointer.resolve()]).toThrow(/Unknown rule/);
    });

    test('it yields a char rule', () => {
      vi.mocked(isGraphPointerRuleChar).mockReturnValue(true);
      const node = new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 2, stepId: 3 });
      const pointer = new GraphPointer(node);
      expect([...pointer.resolve()]).toEqual([pointer]);
    });

    test('it yields a char excluded rule', () => {
      vi.mocked(isGraphPointerRuleCharExclude).mockReturnValue(true);
      const node = new GraphNode(new RuleCharExclude([97]), { stackId: 1, pathId: 2, stepId: 3 });
      const pointer = new GraphPointer(node);
      expect([...pointer.resolve()]).toEqual([pointer]);
    });

    test('it yields an end rule without a parent', () => {
      vi.mocked(isGraphPointerRuleEnd).mockReturnValue(true);
      const node = new GraphNode(new RuleEnd(), { stackId: 1, pathId: 2, stepId: 3 });
      const pointer = new GraphPointer(node);
      expect([...pointer.resolve()]).toEqual([pointer]);
    });

    test('it yields an end rule with a parent', () => {
      vi.mocked(isGraphPointerRuleEnd).mockReturnValue(true);
      const rule = new RuleEnd();
      const parentNode = new GraphNode(rule, { stackId: 2, pathId: 1, stepId: 1 });
      const parentPointer = new GraphPointer(parentNode);
      const childNode = new GraphNode(rule, { stackId: 1, pathId: 1, stepId: 1 });
      const childPointer = new GraphPointer(childNode, parentPointer);
      expect([...childPointer.resolve()]).toEqual([parentPointer]);
    });

    test('it yields an end rule with a grandparent', () => {
      vi.mocked(isGraphPointerRuleEnd).mockReturnValue(true);
      const rule = new RuleEnd();
      const grandparentNode = new GraphNode(rule, { stackId: 2, pathId: 1, stepId: 1 });
      const grandparentPointer = new GraphPointer(grandparentNode);
      const parentNode = new GraphNode(rule, { stackId: 2, pathId: 1, stepId: 1 });
      const parentPointer = new GraphPointer(parentNode, grandparentPointer);
      const childNode = new GraphNode(rule, { stackId: 1, pathId: 1, stepId: 1 });
      const childPointer = new GraphPointer(childNode, parentPointer);
      expect([...childPointer.resolve()]).toEqual([grandparentPointer]);
    });

    test('it yields an end rule with a parent that is not an end, with a grandparent', async () => {
      const actual = await vi.importActual<
        typeof import('../../../src/grammar-graph/type-guards.ts')
      >('../../../src/grammar-graph/type-guards.ts');
      vi.mocked(isGraphPointerRuleEnd).mockImplementation(actual.isGraphPointerRuleEnd);
      vi.mocked(isGraphPointerRuleChar).mockImplementation(actual.isGraphPointerRuleChar);
      const rule = new RuleEnd();
      const grandparentNode = new GraphNode(rule, { stackId: 2, pathId: 1, stepId: 1 });
      const grandparentPointer = new GraphPointer(grandparentNode);
      const parentNode = new GraphNode(new RuleChar([97]), { stackId: 2, pathId: 1, stepId: 1 });
      const parentPointer = new GraphPointer(parentNode, grandparentPointer);
      const childNode = new GraphNode(rule, { stackId: 1, pathId: 1, stepId: 1 });
      const childPointer = new GraphPointer(childNode, parentPointer);
      expect([...childPointer.resolve()]).toEqual([parentPointer]);
    });
  });
});
