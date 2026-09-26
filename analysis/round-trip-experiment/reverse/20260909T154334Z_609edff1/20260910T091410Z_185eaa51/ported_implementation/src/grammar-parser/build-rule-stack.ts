import { isRange, isRuleEnd, Rule } from '../grammar-graph/type-guards';
import { RuleChar, RuleCharExclude, RuleEnd } from '../grammar-graph/types';
import { RuleRef } from '../grammar-graph/rule-ref';
import {
  isRuleDefAlt,
  isRuleDefChar,
  isRuleDefCharAlt,
  isRuleDefCharNot,
  isRuleDefCharRngUpper,
  isRuleDefEnd,
  isRuleDefRef,
} from '../rules-builder/type-guards';
import { InternalRuleDef } from '../rules-builder/types';
import { itemAt } from '../utils/char-at';

const makeCharRule = (ruleDef: InternalRuleDef): RuleChar | RuleCharExclude => {
  const value = [...(ruleDef.value as number[])];
  if (isRuleDefCharNot(ruleDef)) {
    return new RuleCharExclude(value);
  }
  return new RuleChar(value);
};

export const buildRuleStack = (linearRules: InternalRuleDef[]): Rule[][] => {
  let paths: Rule[] = [];

  const stack: Rule[][] = [];

  let idx = 0;
  while (idx < linearRules.length) {
    const ruleDef = linearRules[idx];
    if (isRuleDefChar(ruleDef) || isRuleDefCharNot(ruleDef)) {
      // this could be a single char, or a range, or a sequence of alts;
      // we don't know until we step through it.
      const charRule = makeCharRule(ruleDef);
      idx += 1;
      let rule = itemAt(linearRules, idx);
      while (idx < linearRules.length && (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          if (!charRule.value.length) {
            throw new Error('Unexpected undefined value');
          }
          const prevValue = charRule.value.pop();
          if (isRange(prevValue)) {
            throw new Error(
              `Unexpected range, expected a number but got an array: ${prevValue}`,
            );
          }
          charRule.value.push([prevValue as number, (rule as InternalRuleDef).value as number]);
        }
        if (isRuleDefCharAlt(rule)) {
          charRule.value.push((rule as InternalRuleDef).value as number);
        }
        idx += 1;
        rule = itemAt(linearRules, idx);
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
          `Encountered char alt, should be handled by above block: ${ruleDef.type}`,
        );
      } else {
        throw new Error(`Unsupported rule type: ${ruleDef.type}`);
      }
      idx += 1;
    }
  }

  if (!isRuleEnd(itemAt(paths, paths.length - 1))) {
    paths.push(new RuleEnd());
  }

  stack.push(paths);

  return stack;
};
