import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
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
  describe('is graph pointer rule ref', () => {
    test('it returns true', () => {
      assert.ok(isGraphPointerRuleRef(pointerFor(new RuleRef(1))));
    });

    test('it returns false', () => {
      assert.ok(!isGraphPointerRuleRef(pointerFor(new RuleEnd())));
    });
  });

  describe('is graph pointer rule end', () => {
    test('it returns false', () => {
      assert.ok(!isGraphPointerRuleEnd(pointerFor(new RuleRef(1))));
    });

    test('it returns true', () => {
      assert.ok(isGraphPointerRuleEnd(pointerFor(new RuleEnd())));
    });
  });

  describe('is graph pointer rule char', () => {
    test('it returns true', () => {
      assert.ok(isGraphPointerRuleChar(pointerFor(new RuleChar([97]))));
    });

    test('it returns false', () => {
      assert.ok(!isGraphPointerRuleChar(pointerFor(new RuleEnd())));
    });
  });

  describe('is graph pointer rule char exclude', () => {
    test('it returns true', () => {
      assert.ok(isGraphPointerRuleCharExclude(pointerFor(new RuleCharExclude([97]))));
    });

    test('it returns false', () => {
      assert.ok(!isGraphPointerRuleCharExclude(pointerFor(new RuleChar([97]))));
    });
  });

  describe('is rule', () => {
    test('it returns false for null', () => {
      assert.ok(!isRule(null));
    });

    test('it returns false for a non rule', () => {
      assert.ok(!isRule({ type: 'invalid', value: [] }));
    });

    test('it returns true for valid rule objects', () => {
      assert.ok(isRule(new RuleChar([65, [66, 67] as Range])));
    });
  });

  describe('is rule ref', () => {
    test('it returns true for valid rule refs', () => {
      assert.ok(isRuleRef(new RuleRef(1)));
    });

    test('it returns false for invalid rule refs', () => {
      assert.ok(!isRuleRef(new RuleChar([65])));
    });
  });

  describe('is rule end', () => {
    test('it returns true for valid rule ends', () => {
      assert.ok(isRuleEnd(new RuleEnd()));
    });

    test('it returns false for invalid rule ends', () => {
      assert.ok(!isRuleEnd(new RuleChar([65])));
    });
  });

  describe('is rule char', () => {
    test('it returns true for valid rule chars', () => {
      assert.ok(isRuleChar(new RuleChar([65])));
    });

    test('it returns false for invalid rule chars', () => {
      assert.ok(!isRuleChar(new RuleCharExclude([65])));
    });
  });

  describe('is rule char exclude', () => {
    test('it returns true for valid rule chars', () => {
      assert.ok(isRuleCharExclude(new RuleCharExclude([65])));
    });

    test('it returns false for invalid rule chars', () => {
      assert.ok(!isRuleCharExclude(new RuleChar([65])));
    });
  });

  describe('is range', () => {
    test('it returns true for valid ranges', () => {
      assert.ok(isRange([1, 10]));
    });

    for (const value of [[1, '10'], [1], 5]) {
      test(`it returns false for invalid range ${JSON.stringify(value)}`, () => {
        assert.ok(!isRange(value));
      });
    }
  });
});
