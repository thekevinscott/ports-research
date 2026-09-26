import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { buildRuleStack } from '../../../src/grammar-parser/build-rule-stack.ts';
import { decodeInternalRules, decodeUnresolvedRules, loadFixture } from '../decode-rules.ts';

interface BuildRuleStackCase {
  input: unknown;
  expected: unknown;
}

describe('build rule stack', () => {
  for (const [index, { input, expected }] of loadFixture<BuildRuleStackCase[]>(
    'build_rule_stack_test',
  ).entries()) {
    test(`case ${index}`, () => {
      const linearRules = decodeInternalRules([input])[0];
      assert.deepStrictEqual(
        buildRuleStack(linearRules),
        decodeUnresolvedRules(expected),
      );
    });
  }
});
