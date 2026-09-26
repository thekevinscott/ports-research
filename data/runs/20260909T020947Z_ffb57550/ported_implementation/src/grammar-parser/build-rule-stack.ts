import type {
  Range,
  RuleChar,
  RuleCharExclude,
  UnresolvedRule,
} from '../grammar-graph/grammar-graph-types.js';
import {
  ruleChar,
  ruleCharExclude,
  ruleEnd,
} from '../grammar-graph/grammar-graph-types.js';
import { RuleRef } from '../grammar-graph/rule-ref.js';
import { isRange, isRuleEnd } from '../grammar-graph/type-guards.js';
import {
  isRuleDefAlt,
  isRuleDefChar,
  isRuleDefCharAlt,
  isRuleDefCharNot,
  isRuleDefCharRngUpper,
  isRuleDefEnd,
  isRuleDefRef,
  type InternalRuleDef,
  type InternalRuleDefChar,
  type InternalRuleDefCharNot,
} from '../rules-builder/rules-builder-types.js';

export const makeCharRule = (
  ruleDef: InternalRuleDefChar | InternalRuleDefCharNot,
): RuleChar | RuleCharExclude => {
  const value = ruleDef.value as (number | Range)[];
  if (isRuleDefCharNot(ruleDef)) {
    return ruleCharExclude(value);
  }
  if (isRuleDefChar(ruleDef)) {
    return ruleChar(value);
  }

  throw new Error(
    `Unsupported rule type for make_char_rule: ${JSON.stringify(ruleDef)}`,
  );
};

export const buildRuleStack = (
  linearRules: InternalRuleDef[],
): UnresolvedRule[][] => {
  let paths: UnresolvedRule[] = [];
  const stack: UnresolvedRule[][] = [];
  let idx = 0;

  while (idx < linearRules.length) {
    const ruleDef = linearRules[idx];
    if (isRuleDefChar(ruleDef) || isRuleDefCharNot(ruleDef)) {
      // this could be a single char, or a range, or a sequence of alts; we don't know until we step through it.
      const charRule = makeCharRule(ruleDef);
      idx += 1;
      let rule: InternalRuleDef | undefined = linearRules[idx];
      while (
        idx < linearRules.length &&
        (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))
      ) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          const prevValue = charRule.value.pop();
          if (isRange(prevValue)) {
            throw new Error(
              `Unexpected range, expected a number but got an array: ${JSON.stringify(prevValue)}`,
            );
          }
          if (prevValue === undefined) {
            throw new Error('Unexpected undefined value');
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
        if (paths.length === 0) {
          throw new Error('Encountered alt without anything before it');
        }
        paths.push(ruleEnd());
        stack.push(paths);
        paths = [];
      } else if (isRuleDefEnd(ruleDef)) {
        paths.push(ruleEnd());
      } else if (isRuleDefRef(ruleDef)) {
        paths.push(new RuleRef(ruleDef.value));
      } else if (isRuleDefCharAlt(ruleDef)) {
        throw new Error(
          `Encountered char alt, should be handled by above block: ${JSON.stringify(ruleDef)}`,
        );
      } else {
        throw new Error(`Unsupported rule type: ${JSON.stringify(ruleDef)}`);
      }
      idx += 1;
    }
  }

  if (!isRuleEnd(paths[paths.length - 1])) {
    paths.push(ruleEnd());
  }

  stack.push(paths);
  return stack;
};
