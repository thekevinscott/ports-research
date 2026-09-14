import { RuleRef } from '../grammarGraph/ruleRef.js';
import { isRange, isRuleEnd } from '../grammarGraph/typeGuards.js';
import { ruleChar, ruleCharExclude, ruleEnd } from '../grammarGraph/types.js';
import type { RuleChar, RuleCharExclude, UnresolvedRule } from '../grammarGraph/types.js';
import {
  isRuleDefAlt,
  isRuleDefChar,
  isRuleDefCharAlt,
  isRuleDefCharNot,
  isRuleDefCharRngUpper,
  isRuleDefEnd,
  isRuleDefRef,
} from '../rulesBuilder/typeGuards.js';
import type { InternalRuleDef } from '../rulesBuilder/types.js';

const makeCharRule = (ruleDef: InternalRuleDef): RuleChar | RuleCharExclude => {
  if (isRuleDefCharNot(ruleDef)) {
    return ruleCharExclude([...ruleDef.value]);
  }
  if (!isRuleDefChar(ruleDef)) {
    throw new Error(`Unsupported rule type: ${ruleDef.type}`);
  }
  return ruleChar([...ruleDef.value]);
};

export const buildRuleStack = (linearRules: InternalRuleDef[]): UnresolvedRule[][] => {
  let paths: UnresolvedRule[] = [];

  const stack: UnresolvedRule[][] = [];

  let idx = 0;
  while (idx < linearRules.length) {
    const ruleDef = linearRules[idx];
    if (isRuleDefChar(ruleDef) || isRuleDefCharNot(ruleDef)) {
      // this could be a single char, or a range, or a sequence of alts;
      // we don't know until we step through it.
      const charRule = makeCharRule(ruleDef);
      idx += 1;
      let rule: InternalRuleDef | undefined = linearRules[idx];
      while (idx < linearRules.length && (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          if (!charRule.value.length) {
            throw new Error('Unexpected undefined value');
          }
          const prevValue = charRule.value.pop();
          if (isRange(prevValue)) {
            throw new Error(
              `Unexpected range, expected a number but got an array: ${JSON.stringify(prevValue)}`,
            );
          }
          charRule.value.push([prevValue as number, rule.value]);
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
          `Encountered char alt, should be handled by above block: ${ruleDef.type}`,
        );
      } else {
        throw new Error(`Unsupported rule type: ${ruleDef.type}`);
      }
      idx += 1;
    }
  }

  if (!paths.length || !isRuleEnd(paths[paths.length - 1])) {
    paths.push(ruleEnd());
  }

  stack.push(paths);

  return stack;
};
