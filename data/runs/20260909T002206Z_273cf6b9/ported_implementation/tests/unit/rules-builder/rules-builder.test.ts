import { describe, expect, test } from 'vitest';
import { RulesBuilder } from '../../../src/rules-builder/rules-builder.ts';
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
  type InternalRuleDef,
} from '../../../src/rules-builder/rules-builder-types.ts';
import cases from '../../fixtures/rules-builder.json' with { type: 'json' };

interface RuleDefFixture {
  kind: string;
  value?: number | number[];
}

type Case = [string, string, [[string, number][], RuleDefFixture[][]]];

const buildRuleDef = ({ kind, value }: RuleDefFixture): InternalRuleDef => {
  switch (kind) {
    case 'char':
      return new InternalRuleDefChar(value as number[]);
    case 'char_alt':
      return new InternalRuleDefCharAlt(value as number);
    case 'char_not':
      return new InternalRuleDefCharNot(value as number[]);
    case 'char_rng_upper':
      return new InternalRuleDefCharRngUpper(value as number);
    case 'ref':
      return new InternalRuleDefReference(value as number);
    case 'alt':
      return new InternalRuleDefAlt();
    case 'end':
      return new InternalRuleDefEnd();
    default:
      throw new Error(`Unknown rule def kind: ${kind}`);
  }
};

describe('grammar parser', () => {
  test.each((cases as Case[]).map(([key, grammar, expected]) => [key, grammar, expected] as const))(
    '%s',
    (_key, grammar, expected) => {
      const [symbolIdsExpected, rulesExpected] = expected;
      const parsedGrammar = new RulesBuilder(grammar.replaceAll('\\n', '\n'));
      expect(parsedGrammar.rules).toStrictEqual(rulesExpected.map(rule => rule.map(buildRuleDef)));
      expect([...parsedGrammar.symbolIds.entries()]).toStrictEqual(
        symbolIdsExpected.map(([name, id]) => [name, id]),
      );
    },
  );
});
