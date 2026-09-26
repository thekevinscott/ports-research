import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { RuleChar, RuleCharExclude, RuleEnd } from '../src/grammarGraph/grammarGraphTypes.ts';
import type { UnresolvedRule } from '../src/grammarGraph/grammarGraphTypes.ts';
import { GraphNode } from '../src/grammarGraph/graphNode.ts';
import { GraphPointer } from '../src/grammarGraph/graphPointer.ts';
import { RuleRef } from '../src/grammarGraph/ruleRef.ts';
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
} from '../src/grammarGraph/typeGuards.ts';

const META = { stackId: 1, pathId: 2, stepId: 3 };
const pointerFor = (rule: UnresolvedRule): GraphPointer =>
  new GraphPointer(new GraphNode(rule, META));

describe('rule type guards', () => {
  describe('isGraphPointerRuleRef', () => {
    it('returns true', () => {
      assert.ok(isGraphPointerRuleRef(pointerFor(new RuleRef(1))));
    });

    it('returns false', () => {
      assert.ok(!isGraphPointerRuleRef(pointerFor(new RuleEnd())));
    });
  });

  describe('isGraphPointerRuleEnd', () => {
    it('returns false', () => {
      assert.ok(!isGraphPointerRuleEnd(pointerFor(new RuleRef(1))));
    });

    it('returns true', () => {
      assert.ok(isGraphPointerRuleEnd(pointerFor(new RuleEnd())));
    });
  });

  describe('isGraphPointerRuleChar', () => {
    it('returns true', () => {
      assert.ok(isGraphPointerRuleChar(pointerFor(new RuleChar([97]))));
    });

    it('returns false', () => {
      assert.ok(!isGraphPointerRuleChar(pointerFor(new RuleEnd())));
    });
  });

  describe('isGraphPointerRuleCharExclude', () => {
    it('returns true', () => {
      assert.ok(isGraphPointerRuleCharExclude(pointerFor(new RuleCharExclude([97]))));
    });

    it('returns false', () => {
      assert.ok(!isGraphPointerRuleCharExclude(pointerFor(new RuleChar([97]))));
    });
  });

  describe('isRule', () => {
    it('returns false for null', () => {
      assert.ok(!isRule(null));
    });

    it('returns false for a non-rule', () => {
      assert.ok(!isRule({ type: 'invalid', value: [] }));
    });

    it('returns true for valid rule objects', () => {
      assert.ok(isRule(new RuleChar([65, 66, 67])));
    });
  });

  describe('isRuleRef', () => {
    it('returns true for valid rule refs', () => {
      assert.ok(isRuleRef(new RuleRef(1)));
    });

    it('returns false for invalid rule refs', () => {
      assert.ok(!isRuleRef(new RuleChar([65])));
    });
  });

  describe('isRuleEnd', () => {
    it('returns true for valid rule ends', () => {
      assert.ok(isRuleEnd(new RuleEnd()));
    });

    it('returns false for invalid rule ends', () => {
      assert.ok(!isRuleEnd(new RuleChar([65])));
    });
  });

  describe('isRuleChar', () => {
    it('returns true for valid rule chars', () => {
      assert.ok(isRuleChar(new RuleChar([65])));
    });

    it('returns false for invalid rule chars', () => {
      assert.ok(!isRuleChar(new RuleCharExclude([65])));
    });
  });

  describe('isRuleCharExclude', () => {
    it('returns true for valid rule char excludes', () => {
      assert.ok(isRuleCharExclude(new RuleCharExclude([65])));
    });

    it('returns false for invalid rule char excludes', () => {
      assert.ok(!isRuleCharExclude(new RuleChar([65])));
    });
  });

  describe('isRange', () => {
    it('returns true for valid ranges', () => {
      assert.ok(isRange([1, 10]));
    });

    for (const value of [[1, '10'], [1], 5]) {
      it(`returns false for the invalid range ${JSON.stringify(value)}`, () => {
        assert.ok(!isRange(value));
      });
    }
  });
});

describe('RuleRef', () => {
  it('initializes with a given value', () => {
    assert.equal(new RuleRef(123).value, 123);
  });

  it('allows setting and getting nodes', () => {
    const mockNodes = new Set([new GraphNode(new RuleEnd(), META)]);
    const ruleRef = new RuleRef(123);
    ruleRef.nodes = mockNodes;
    assert.equal(ruleRef.nodes, mockNodes);
  });

  it('throws an error if trying to get nodes before setting them', () => {
    const ruleRef = new RuleRef(123);
    assert.throws(() => ruleRef.nodes, /Nodes are not set/u);
  });
});
