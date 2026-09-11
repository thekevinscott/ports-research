import { RuleRef } from '../grammarGraph/ruleRef.js';
import { isRange, isRuleEnd, type GraphRule } from '../grammarGraph/typeGuards.js';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type RuleCharValue,
} from '../grammarGraph/types.js';
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
  const value = [...(ruleDef.value as number[])] as RuleCharValue;
  return isRuleDefCharNot(ruleDef)
    ? new RuleCharExclude(value)
    : new RuleChar(value);
};

export const buildRuleStack = (
  linearRules: InternalRuleDef[]
): GraphRule[][] => {
  const stack: GraphRule[][] = [];
  let paths: GraphRule[] = [];

  let idx = 0;
  while (idx < linearRules.length) {
    const ruleDef = linearRules[idx];
    if (isRuleDefChar(ruleDef) || isRuleDefCharNot(ruleDef)) {
      // this could be a single char, or a range, or a sequence of alts; we don't
      // know until we step through it.
      const charRule = makeCharRule(ruleDef);
      idx += 1;
      let rule: InternalRuleDef | undefined =
        idx < linearRules.length ? linearRules[idx] : undefined;
      while (
        idx < linearRules.length &&
        (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))
      ) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          const prevValue = charRule.value.length
            ? charRule.value.pop()
            : undefined;
          if (isRange(prevValue)) {
            throw new Error(
              `Unexpected range, expected a number but got an array: ${JSON.stringify(
                prevValue
              )}`
            );
          }
          if (prevValue === undefined) {
            throw new Error('Unexpected undefined value');
          }
          const range: Range = [
            prevValue,
            (rule as InternalRuleDef).value as number,
          ];
          charRule.value.push(range);
        }
        if (isRuleDefCharAlt(rule)) {
          charRule.value.push((rule as InternalRuleDef).value as number);
        }
        idx += 1;
        rule = idx < linearRules.length ? linearRules[idx] : undefined;
      }
      paths.push(charRule);
    } else {
      if (isRuleDefAlt(ruleDef)) {
        if (!paths.length) {
          throw new Error('Encountered alt without anything before it');
        }
        paths.push(new RuleEnd());
        stack.push(paths);
        paths = [];
      } else if (isRuleDefEnd(ruleDef)) {
        paths.push(new RuleEnd());
      } else if (isRuleDefRef(ruleDef)) {
        paths.push(new RuleRef(ruleDef.value as number));
      } else if (isRuleDefCharAlt(ruleDef)) {
        throw new Error(
          `Encountered char alt, should be handled by above block: ${ruleDef.type}`
        );
      } else {
        throw new Error(`Unsupported rule type: ${ruleDef.type}`);
      }
      idx += 1;
    }
  }

  if (!paths.length || !isRuleEnd(paths[paths.length - 1])) {
    paths.push(new RuleEnd());
  }

  stack.push(paths);

  return stack;
};
