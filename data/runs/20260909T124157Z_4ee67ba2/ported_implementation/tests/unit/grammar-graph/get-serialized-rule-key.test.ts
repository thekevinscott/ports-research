import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import {
  KEY_TRANSLATION,
  getSerializedRuleKey,
} from '../../../src/grammar-graph/get-serialized-rule-key.ts';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type UnresolvedRule,
} from '../../../src/grammar-graph/grammar-graph-types.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';

// The reference suite forces each branch with mocked type guards; the real guards
// select the same branches for these inputs, so the port asserts against them directly.
describe('get serialized rule key', () => {
  test('returns type for end rules', () => {
    assert.equal(getSerializedRuleKey(new RuleEnd()), `${KEY_TRANSLATION[RuleEnd.name]}`);
  });

  test('returns type and value for character rules', () => {
    assert.equal(
      getSerializedRuleKey(new RuleChar([97])),
      `${KEY_TRANSLATION[RuleChar.name]}-[97]`,
    );
  });

  test('returns type and value for character exclude rules', () => {
    assert.equal(
      getSerializedRuleKey(new RuleCharExclude([97])),
      `${KEY_TRANSLATION[RuleCharExclude.name]}-[97]`,
    );
  });

  test('returns ref type with value for reference rules', () => {
    assert.equal(getSerializedRuleKey(new RuleRef(99)), '3-99');
  });

  test('throws error for unknown rule types', () => {
    const rule = { type: 'UNKNOWN', value: 'something' } as unknown as UnresolvedRule;
    assert.throws(() => getSerializedRuleKey(rule), /Unknown rule type/);
  });
});
