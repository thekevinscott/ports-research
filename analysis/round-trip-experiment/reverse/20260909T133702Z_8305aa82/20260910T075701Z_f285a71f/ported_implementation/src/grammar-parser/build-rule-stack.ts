import { RuleRef } from '../grammar-graph/rule-ref.js';
import { isRange, isRuleEnd, type Rule } from '../grammar-graph/type-guards.js';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type RuleCharValue,
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

const makeCharRule = (
  ruleDef: InternalRuleDef,
): RuleChar | RuleCharExclude => {
  const value = ruleDef.value as number[];
  if (isRuleDefCharNot(ruleDef)) {
    return new RuleCharExclude([...value]);
  }
  return new RuleChar([...value]);
};

export const buildRuleStack = (
  linearRules: InternalRuleDef[],
): Rule[][] => {
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
      let rule: InternalRuleDef | undefined =
        idx < linearRules.length ? linearRules[idx] : undefined;
      while (
        idx < linearRules.length &&
        (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))
      ) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          const prevValue: RuleCharValue | undefined = charRule.value.length
            ? charRule.value.pop()
            : undefined;
          if (isRange(prevValue)) {
            throw new Error(
              `Unexpected range, expected a number but got an array: ${JSON.stringify(
                prevValue,
              )}`,
            );
          }
          if (prevValue === undefined) {
            throw new Error('Unexpected undefined value');
          }
          charRule.value.push([prevValue, (rule as InternalRuleDef).value as number]);
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
          `Encountered char alt, should be handled by above block: ${ruleDef.type}`,
        );
      } else {
        throw new Error(`Unsupported rule type: ${ruleDef.type}`);
      }
      idx += 1;
    }
  }

  if (!isRuleEnd(paths.length ? paths[paths.length - 1] : undefined)) {
    paths.push(new RuleEnd());
  }

  stack.push(paths);

  return stack;
};
