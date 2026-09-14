import { RuleRef } from '../grammarGraph/ruleRef';
import { isRange, isRuleEnd } from '../grammarGraph/typeGuards';
import { RuleChar, RuleCharExclude, RuleEnd } from '../grammarGraph/types';
import type { Range, UnresolvedRule } from '../grammarGraph/types';
import {
  isRuleDefAlt,
  isRuleDefChar,
  isRuleDefCharAlt,
  isRuleDefCharNot,
  isRuleDefCharRngUpper,
  isRuleDefEnd,
  isRuleDefRef,
} from '../rulesBuilder/typeGuards';
import type {
  InternalRuleDef,
  InternalRuleDefChar,
  InternalRuleDefCharNot,
} from '../rulesBuilder/types';

const makeCharRule = (
  ruleDef: InternalRuleDefChar | InternalRuleDefCharNot,
): RuleChar | RuleCharExclude =>
  isRuleDefCharNot(ruleDef)
    ? new RuleCharExclude([...ruleDef.value])
    : new RuleChar([...ruleDef.value]);

export const buildRuleStack = (
  linearRules: InternalRuleDef[],
): UnresolvedRule[][] => {
  const stack: UnresolvedRule[][] = [];
  let paths: UnresolvedRule[] = [];

  let idx = 0;
  while (idx < linearRules.length) {
    const ruleDef = linearRules[idx];
    if (isRuleDefChar(ruleDef) || isRuleDefCharNot(ruleDef)) {
      // this could be a single char, or a range, or a sequence of alts;
      // we don't know until we step through it.
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
          charRule.value.push([prevValue, rule.value] as Range);
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
        paths.push(new RuleEnd());
        stack.push(paths);
        paths = [];
      } else if (isRuleDefEnd(ruleDef)) {
        paths.push(new RuleEnd());
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

  if (!(paths.length && isRuleEnd(paths[paths.length - 1]))) {
    paths.push(new RuleEnd());
  }

  stack.push(paths);

  return stack;
};
