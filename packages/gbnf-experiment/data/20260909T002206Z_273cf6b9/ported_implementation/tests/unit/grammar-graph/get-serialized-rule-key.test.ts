import { beforeEach, describe, expect, test, vi } from 'vitest';
import {
  KEY_TRANSLATION,
  getSerializedRuleKey,
} from '../../../src/grammar-graph/get-serialized-rule-key.ts';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from '../../../src/grammar-graph/grammar-graph-types.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';
import {
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from '../../../src/grammar-graph/type-guards.ts';

vi.mock('../../../src/grammar-graph/type-guards.ts', async importOriginal => {
  const actual = await importOriginal<
    typeof import('../../../src/grammar-graph/type-guards.ts')
  >();
  return {
    ...actual,
    isRuleEnd: vi.fn(() => false),
    isRuleChar: vi.fn(() => false),
    isRuleCharExclude: vi.fn(() => false),
    isRuleRef: vi.fn(() => false),
  };
});

beforeEach(() => {
  for (const guard of [isRuleEnd, isRuleChar, isRuleCharExclude, isRuleRef]) {
    vi.mocked(guard).mockReturnValue(false);
  }
});

describe('get_serialized_rule_key', () => {
  test('returns type for end rules', () => {
    vi.mocked(isRuleEnd).mockReturnValue(true);
    expect(getSerializedRuleKey(new RuleEnd())).toBe(`${KEY_TRANSLATION.RuleEnd}`);
  });

  test('returns type and value for character rules', () => {
    vi.mocked(isRuleChar).mockReturnValue(true);
    expect(getSerializedRuleKey(new RuleChar([97]))).toBe(`${KEY_TRANSLATION.RuleChar}-[97]`);
  });

  test('returns type and value for character exclude rules', () => {
    vi.mocked(isRuleCharExclude).mockReturnValue(true);
    expect(getSerializedRuleKey(new RuleCharExclude([97]))).toBe(
      `${KEY_TRANSLATION.RuleCharExclude}-[97]`,
    );
  });

  test('returns ref type with value for reference rules', () => {
    vi.mocked(isRuleRef).mockReturnValue(true);
    expect(getSerializedRuleKey(new RuleRef(99))).toBe('3-99');
  });

  test('throws error for unknown rule types', () => {
    const rule = { type: 'UNKNOWN', value: 'something' };
    expect(() => getSerializedRuleKey(rule as never)).toThrow(/Unknown rule type/);
  });
});
