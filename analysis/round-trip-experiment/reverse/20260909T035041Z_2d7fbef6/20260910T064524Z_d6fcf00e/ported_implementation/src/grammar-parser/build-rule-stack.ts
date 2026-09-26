import { RuleRef } from '../grammar-graph/rule-ref.js';
import { isRange, isRuleEnd } from '../grammar-graph/type-guards.js';
import {
  Range,
  RuleChar,
  RuleCharExclude,
  RuleType,
  UnresolvedRule,
} from '../grammar-graph/types.js';
import {
  isRuleDefAlt,
  isRuleDefChar,
  isRuleDefCharAlt,
  isRuleDefCharNot,
  isRuleDefCharRngUpper,
  isRuleDefEnd,
  isRuleDefRef,
} from '../rules-builder/type-guards.js';
import type { InternalRuleDef } from '../rules-builder/types.js';
import { GBNFError } from '../utils/errors/gbnf-error.js';

const makeCharRule = (ruleDef: InternalRuleDef): RuleChar | RuleCharExclude => {
  if (isRuleDefCharNot(ruleDef)) {
    return { type: RuleType.CHAR_EXCLUDE, value: [...ruleDef.value] };
  }
  if (!isRuleDefChar(ruleDef)) {
    throw new GBNFError(`Unsupported rule type: ${ruleDef.type}`);
  }
  return { type: RuleType.CHAR, value: [...ruleDef.value] };
};

export const buildRuleStack = (linearRules: InternalRuleDef[]): UnresolvedRule[][] => {
  let paths: UnresolvedRule[] = [];

  const stack: UnresolvedRule[][] = [];

  let idx = 0;
  while (idx < linearRules.length) {
    const ruleDef = linearRules[idx];
    if (isRuleDefChar(ruleDef) || isRuleDefCharNot(ruleDef)) {
      // this could be a single char, or a range, or a sequence of alts; we don't know
      // until we step through it.
      const charRule = makeCharRule(ruleDef);
      idx += 1;
      let rule: InternalRuleDef | undefined = linearRules[idx];
      while (idx < linearRules.length && (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          const prevValue: number | Range | undefined = charRule.value.pop();
          if (isRange(prevValue)) {
            throw new GBNFError(
              `Unexpected range, expected a number but got an array: ${prevValue}`,
            );
          }
          if (prevValue === undefined) {
            throw new GBNFError('Unexpected undefined value');
          }
          charRule.value.push([prevValue, rule.value]);
        }
        if (isRuleDefCharAlt(rule)) {
          charRule.value.push(rule.value);
        }
        idx += 1;
        rule = linearRules[idx];
      }
      paths.push(charRule);
    } else {
      if (isRuleDefAlt(ruleDef)) {
        if (!paths.length) {
          throw new GBNFError('Encountered alt without anything before it');
        }
        paths.push({ type: RuleType.END });
        stack.push(paths);
        paths = [];
      } else if (isRuleDefEnd(ruleDef)) {
        paths.push({ type: RuleType.END });
      } else if (isRuleDefRef(ruleDef)) {
        paths.push(new RuleRef(ruleDef.value));
      } else if (isRuleDefCharAlt(ruleDef)) {
        throw new GBNFError(
          `Encountered char alt, should be handled by above block: ${ruleDef.type}`,
        );
      } else {
        throw new GBNFError(`Unsupported rule type: ${ruleDef.type}`);
      }
      idx += 1;
    }
  }

  if (!isRuleEnd(paths[paths.length - 1])) {
    paths.push({ type: RuleType.END });
  }

  stack.push(paths);

  return stack;
};
