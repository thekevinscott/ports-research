import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type UnresolvedRule,
} from '../../src/grammar-graph/grammar-graph-types.ts';
import { RuleRef } from '../../src/grammar-graph/rule-ref.ts';
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
  type InternalRuleDef,
} from '../../src/rules-builder/rules-builder-types.ts';

const FIXTURES = join(dirname(fileURLToPath(import.meta.url)), '..', 'fixtures');

export interface TaggedRule {
  cls: string;
  value?: unknown;
}

type Ctor = (value: never) => unknown;

const WITH_VALUE: Record<string, Ctor> = {
  InternalRuleDefChar: (value: number[]) => new InternalRuleDefChar(value),
  InternalRuleDefCharNot: (value: number[]) => new InternalRuleDefCharNot(value),
  InternalRuleDefCharAlt: (value: number) => new InternalRuleDefCharAlt(value),
  InternalRuleDefCharRngUpper: (value: number) => new InternalRuleDefCharRngUpper(value),
  InternalRuleDefReference: (value: number) => new InternalRuleDefReference(value),
  RuleChar: (value: (number | Range)[]) => new RuleChar(value),
  RuleCharExclude: (value: (number | Range)[]) => new RuleCharExclude(value),
  RuleRef: (value: number) => new RuleRef(value),
} as Record<string, Ctor>;

const WITHOUT_VALUE: Record<string, () => unknown> = {
  InternalRuleDefAlt: () => new InternalRuleDefAlt(),
  InternalRuleDefEnd: () => new InternalRuleDefEnd(),
  RuleEnd: () => new RuleEnd(),
};

/** Rebuild the rule objects that the extractor tagged as `{cls, value}`. */
export const decodeRule = (tagged: unknown): unknown => {
  if (Array.isArray(tagged)) {
    return tagged.map(decodeRule);
  }
  if (tagged === null || typeof tagged !== 'object') {
    return tagged;
  }
  const { cls, value } = tagged as TaggedRule;
  const withValue = WITH_VALUE[cls];
  if (withValue) {
    return withValue(value as never);
  }
  const withoutValue = WITHOUT_VALUE[cls];
  if (withoutValue) {
    return withoutValue();
  }
  throw new Error(`Unknown serialized rule class: ${cls}`);
};

export const decodeInternalRules = (tagged: unknown): InternalRuleDef[][] =>
  decodeRule(tagged) as InternalRuleDef[][];

export const decodeUnresolvedRules = (tagged: unknown): UnresolvedRule[][] =>
  decodeRule(tagged) as UnresolvedRule[][];

export const loadFixture = <T>(name: string): T =>
  JSON.parse(readFileSync(join(FIXTURES, `${name}.json`), 'utf-8')) as T;
