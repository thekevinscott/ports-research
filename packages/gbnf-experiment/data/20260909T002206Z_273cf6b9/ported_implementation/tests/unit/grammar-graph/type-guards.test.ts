import { describe, expect, test } from 'vitest';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from '../../../src/grammar-graph/grammar-graph-types.ts';
import { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import { GraphPointer } from '../../../src/grammar-graph/graph-pointer.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRange,
  isRule,
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from '../../../src/grammar-graph/type-guards.ts';

const META = { stackId: 1, pathId: 2, stepId: 3 };

const pointerFor = (rule: RuleChar | RuleCharExclude | RuleEnd | RuleRef): GraphPointer =>
  new GraphPointer(new GraphNode(rule, META));

describe('rule type guards', () => {
  describe('is_graph_pointer_rule_ref', () => {
    test('it returns true', () => {
      expect(isGraphPointerRuleRef(pointerFor(new RuleRef(1)))).toBe(true);
    });

    test('it returns false', () => {
      expect(isGraphPointerRuleRef(pointerFor(new RuleEnd()))).toBe(false);
    });
  });

  describe('is_graph_pointer_rule_end', () => {
    test('it returns false', () => {
      expect(isGraphPointerRuleEnd(pointerFor(new RuleRef(1)))).toBe(false);
    });

    test('it returns true', () => {
      expect(isGraphPointerRuleEnd(pointerFor(new RuleEnd()))).toBe(true);
    });
  });

  describe('is_graph_pointer_rule_char', () => {
    test('it returns true', () => {
      expect(isGraphPointerRuleChar(pointerFor(new RuleChar([97])))).toBe(true);
    });

    test('it returns false', () => {
      expect(isGraphPointerRuleChar(pointerFor(new RuleEnd()))).toBe(false);
    });
  });

  describe('is_graph_pointer_rule_char_exclude', () => {
    test('it returns true', () => {
      expect(isGraphPointerRuleCharExclude(pointerFor(new RuleCharExclude([97])))).toBe(true);
    });

    test('it returns false', () => {
      expect(isGraphPointerRuleCharExclude(pointerFor(new RuleChar([97])))).toBe(false);
    });
  });

  describe('is_rule', () => {
    test('it returns false for null', () => {
      expect(isRule(null)).toBe(false);
    });

    test('it returns false for a non rule', () => {
      expect(isRule({ type: 'invalid', value: [] })).toBe(false);
    });

    test('it returns true for valid rule objects', () => {
      expect(isRule(new RuleChar([65, [66, 67]]))).toBe(true);
    });
  });

  describe('is_rule_ref', () => {
    test('it returns true for valid rule refs', () => {
      expect(isRuleRef(new RuleRef(1))).toBe(true);
    });

    test('it returns false for invalid rule refs', () => {
      expect(isRuleRef(new RuleChar([65]))).toBe(false);
    });
  });

  describe('is_rule_end', () => {
    test('it returns true for valid rule ends', () => {
      expect(isRuleEnd(new RuleEnd())).toBe(true);
    });

    test('it returns false for invalid rule ends', () => {
      expect(isRuleEnd(new RuleChar([65]))).toBe(false);
    });
  });

  describe('is_rule_char', () => {
    test('it returns true for valid rule chars', () => {
      expect(isRuleChar(new RuleChar([65]))).toBe(true);
    });

    test('it returns false for invalid rule chars', () => {
      expect(isRuleChar(new RuleCharExclude([65]))).toBe(false);
    });
  });

  describe('is_rule_char_exclude', () => {
    test('it returns true for valid rule chars', () => {
      expect(isRuleCharExclude(new RuleCharExclude([65]))).toBe(true);
    });

    test('it returns false for invalid rule chars', () => {
      expect(isRuleCharExclude(new RuleChar([65]))).toBe(false);
    });
  });

  describe('is_range', () => {
    test('it returns true for valid ranges', () => {
      expect(isRange([1, 10])).toBe(true);
    });

    test.each([
      [[1, '10']],
      [[1]],
      [5],
    ])('it returns false for invalid range %j', value => {
      expect(isRange(value)).toBe(false);
    });
  });
});
