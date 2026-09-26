import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type UnresolvedRule,
} from '../grammarGraph/grammarGraphTypes.js';
import { RuleRef } from '../grammarGraph/ruleRef.js';
import { isRange, isRuleEnd } from '../grammarGraph/typeGuards.js';
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
} from '../rulesBuilder/rulesBuilderTypes.js';

export const makeCharRule = (
  ruleDef: InternalRuleDefChar | InternalRuleDefCharNot,
): RuleChar | RuleCharExclude => {
  const value = ruleDef.value as (number | Range)[];
  if (isRuleDefCharNot(ruleDef)) {
    return new RuleCharExclude(value);
  }
  if (isRuleDefChar(ruleDef)) {
    return new RuleChar(value);
  }

  throw new Error(`Unsupported rule type for make_char_rule: ${ruleDef}`);
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
      // this could be a single char, or a range, or a sequence of alts; we don't know until we
      // step through it.
      const charRule = makeCharRule(ruleDef);
      idx += 1;
      let rule: InternalRuleDef | null = idx < linearRules.length ? linearRules[idx] : null;
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
        rule = idx < linearRules.length ? linearRules[idx] : null;
      }
      paths.push(charRule);
    } else {
      if (isRuleDefAlt(ruleDef)) {
        if (paths.length === 0) {
          throw new Error('Encountered alt without anything before it');
        }
        paths.push(new RuleEnd());
        stack.push(paths);
        paths = [];
      } else if (isRuleDefEnd(ruleDef)) {
        paths.push(new RuleEnd());
      } else if (isRuleDefRef(ruleDef)) {
        paths.push(new RuleRef(ruleDef.value));
      } else if (isRuleDefCharAlt(ruleDef)) {
        throw new Error(
          `Encountered char alt, should be handled by above block: ${ruleDef}`,
        );
      } else {
        throw new Error(`Unsupported rule type: ${ruleDef}`);
      }
      idx += 1;
    }
  }

  if (!isRuleEnd(paths[paths.length - 1])) {
    paths.push(new RuleEnd());
  }

  stack.push(paths);
  return stack;
};
