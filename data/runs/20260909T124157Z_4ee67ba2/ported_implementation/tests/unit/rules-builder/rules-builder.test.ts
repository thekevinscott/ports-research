import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { RulesBuilder } from '../../../src/rules-builder/rules-builder.ts';
import { decodeInternalRules, loadFixture } from '../decode-rules.ts';

interface RulesBuilderCase {
  key: string;
  grammar: string;
  symbolIds: [string, number][];
  rules: unknown;
}

describe('rules builder', () => {
  for (const { key, grammar, symbolIds, rules } of loadFixture<RulesBuilderCase[]>(
    'rules_builder_test',
  )) {
    test(key, () => {
      const parsedGrammar = new RulesBuilder(grammar.replaceAll('\\n', '\n'));
      assert.deepStrictEqual(parsedGrammar.rules, decodeInternalRules(rules));
      assert.deepStrictEqual([...parsedGrammar.symbolIds.items()], symbolIds);
    });
  }
});
