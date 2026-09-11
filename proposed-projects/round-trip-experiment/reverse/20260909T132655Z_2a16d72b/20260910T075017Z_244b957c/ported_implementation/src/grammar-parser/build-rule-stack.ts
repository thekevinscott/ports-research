import { RuleRef } from '../grammar-graph/rule-ref.js';
import { isRange, isRuleEnd } from '../grammar-graph/type-guards.js';
import {
  Range,
  Rule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
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

const makeCharRule = (ruleDef: InternalRuleDef): RuleChar | RuleCharExclude => {
  const value = [...(ruleDef.value as number[])];
  if (isRuleDefCharNot(ruleDef)) {
    return new RuleCharExclude(value);
  }
  return new RuleChar(value);
};

export const buildRuleStack = (
  linearRules?: InternalRuleDef[]
): (Rule | RuleRef)[][] => {
  let paths: (Rule | RuleRef)[] = [];
  const stack: (Rule | RuleRef)[][] = [];

  const rules = linearRules ?? [];

  let idx = 0;
  while (idx < rules.length) {
    const ruleDef = rules[idx];
    if (isRuleDefChar(ruleDef) || isRuleDefCharNot(ruleDef)) {
      // this could be a single char, or a range, or a sequence of alts; we don't
      // know until we step through it.
      const charRule = makeCharRule(ruleDef);
      idx += 1;
      let rule: InternalRuleDef | undefined =
        idx < rules.length ? rules[idx] : undefined;
      while (
        idx < rules.length &&
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
          charRule.value.push([
            prevValue as number,
            (rule as InternalRuleDef).value as number,
          ] as Range);
        }
        if (isRuleDefCharAlt(rule)) {
          charRule.value.push((rule as InternalRuleDef).value as number);
        }
        idx += 1;
        rule = idx < rules.length ? rules[idx] : undefined;
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

  if (!isRuleEnd(paths.length ? paths[paths.length - 1] : undefined)) {
    paths.push(new RuleEnd());
  }

  stack.push(paths);

  return stack;
};
