import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { Color, colorize } from '../src/grammarGraph/colorize.ts';
import { getInputAsCodePoints } from '../src/grammarGraph/getInputAsCodePoints.ts';
import { getParentStackId } from '../src/grammarGraph/getParentStackId.ts';
import {
  KEY_TRANSLATION,
  getSerializedRuleKey,
} from '../src/grammarGraph/getSerializedRuleKey.ts';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from '../src/grammarGraph/grammarGraphTypes.ts';
import type { UnresolvedRule } from '../src/grammarGraph/grammarGraphTypes.ts';
import { GraphNode } from '../src/grammarGraph/graphNode.ts';
import { GraphPointer } from '../src/grammarGraph/graphPointer.ts';
import { RuleRef } from '../src/grammarGraph/ruleRef.ts';

describe('colorize', () => {
  it('colorizes strings', () => {
    assert.equal(colorize('hello', Color.BLUE), '\x1b[34mhello');
    assert.equal(colorize('test', Color.CYAN), '\x1b[36mtest');
    assert.equal(colorize('example', Color.GREEN), '\x1b[32mexample');
  });

  it('colorizes numbers', () => {
    assert.equal(colorize(123, Color.RED), '\x1b[31m123');
    assert.equal(colorize(456, Color.GRAY), '\x1b[90m456');
    assert.equal(colorize(789, Color.YELLOW), '\x1b[33m789');
  });
});

describe('getInputAsCodePoints', () => {
  it('returns code points for a string', () => {
    assert.deepStrictEqual(getInputAsCodePoints('abc'), [97, 98, 99]);
  });

  it('returns code points for a number', () => {
    assert.deepStrictEqual(getInputAsCodePoints(99), [99]);
  });

  it('returns code points for an array of numbers', () => {
    assert.deepStrictEqual(getInputAsCodePoints([99, 100, 101]), [99, 100, 101]);
  });
});

describe('getParentStackId', () => {
  const s = (str: string): string => JSON.stringify(str);
  const mockColorize = (text: string | number, color: string): string => `[${s(color)}]:${text}`;
  const red = s(Color.RED);
  const gray = s(Color.GRAY);

  const createMockPointer = (
    stackId: number,
    pathId: number,
    stepId: number,
    parent: GraphPointer | null = null,
  ): GraphPointer => new GraphPointer(new GraphNode(new RuleEnd(), { stackId, pathId, stepId }), parent);

  it('returns an empty string if there are no parents', () => {
    assert.equal(getParentStackId(createMockPointer(1, 1, 1), mockColorize), '');
  });

  it('returns a single parent id, colored correctly', () => {
    const parentPointer = createMockPointer(1, 1, 1);
    const pointer = createMockPointer(2, 2, 2, parentPointer);
    assert.equal(getParentStackId(pointer, mockColorize), `[${red}]:1,1,1`);
  });

  it('returns multiple parent ids separated by colored arrows', () => {
    const grandparentPointer = createMockPointer(0, 0, 0);
    const parentPointer = createMockPointer(1, 1, 1, grandparentPointer);
    const pointer = createMockPointer(2, 2, 2, parentPointer);
    assert.equal(
      getParentStackId(pointer, mockColorize),
      `[${red}]:1,1,1[${gray}]:<-[${red}]:0,0,0`,
    );
  });

  it('handles deep nesting of pointers', () => {
    const greatGrandparentPointer = createMockPointer(0, 0, 0);
    const grandparentPointer = createMockPointer(1, 1, 1, greatGrandparentPointer);
    const parentPointer = createMockPointer(2, 2, 2, grandparentPointer);
    const pointer = createMockPointer(3, 3, 3, parentPointer);
    assert.equal(
      getParentStackId(pointer, mockColorize),
      `[${red}]:2,2,2[${gray}]:<-[${red}]:1,1,1[${gray}]:<-[${red}]:0,0,0`,
    );
  });
});

describe('getSerializedRuleKey', () => {
  it('returns the type for end rules', () => {
    assert.equal(getSerializedRuleKey(new RuleEnd()), `${KEY_TRANSLATION.get(RuleEnd)}`);
  });

  it('returns the type and value for character rules', () => {
    assert.equal(
      getSerializedRuleKey(new RuleChar([97])),
      `${KEY_TRANSLATION.get(RuleChar)}-[97]`,
    );
  });

  it('returns the type and value for character exclude rules', () => {
    assert.equal(
      getSerializedRuleKey(new RuleCharExclude([97])),
      `${KEY_TRANSLATION.get(RuleCharExclude)}-[97]`,
    );
  });

  it('returns the ref type with the value for reference rules', () => {
    assert.equal(getSerializedRuleKey(new RuleRef(99)), '3-99');
  });

  it('serializes ranges the same way Python json.dumps does', () => {
    assert.equal(getSerializedRuleKey(new RuleChar([[97, 122], 95])), '1-[[97, 122], 95]');
  });

  it('throws an error for unknown rule types', () => {
    const rule = { type: 'UNKNOWN', value: 'something' } as unknown as UnresolvedRule;
    assert.throws(
      () => getSerializedRuleKey(rule),
      /Unknown rule type: \{'type': 'UNKNOWN', 'value': 'something'\}/u,
    );
  });
});
