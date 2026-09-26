import { RuleChar, RuleCharExclude, RuleEnd } from '../src/index.ts';
import type { Range, ResolvedRule } from '../src/index.ts';

export interface ExpectedRule {
  type: string;
  value?: (number | Range)[];
}

/** Mirrors `transformed_expected_dict` in the Python suite. */
export const transformedExpectedDict = (e: ExpectedRule): ResolvedRule => {
  if (e.type === 'char') {
    return new RuleChar(e.value as (number | Range)[]);
  }
  if (e.type === 'char_exclude') {
    return new RuleCharExclude(e.value as (number | Range)[]);
  }
  if (e.type === 'end') {
    return new RuleEnd();
  }
  throw new Error(`Unknown type found in expectation array: ${e.type}`);
};

/** Mirrors `sorted(rules, key=lambda r: json.dumps(r.__dict__))`. */
export const sortRules = (rules: Iterable<ResolvedRule>): ResolvedRule[] =>
  [...rules].sort((a, b) => {
    const left = JSON.stringify(a.dict);
    const right = JSON.stringify(b.dict);
    if (left < right) {
      return -1;
    }
    return left > right ? 1 : 0;
  });

/** A stable, readable label for a parametrized case. */
export const label = (...values: unknown[]): string =>
  values.map(value => JSON.stringify(value)).join(', ');
