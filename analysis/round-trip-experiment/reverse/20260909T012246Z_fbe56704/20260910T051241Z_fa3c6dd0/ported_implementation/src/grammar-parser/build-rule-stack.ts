import { RuleRef } from '../grammar-graph/rule-ref.ts';
import { isRange, isRuleEnd } from '../grammar-graph/type-guards.ts';
import { RuleChar, RuleCharExclude, RuleEnd } from '../grammar-graph/types.ts';
import type { Range, UnresolvedRule } from '../grammar-graph/types.ts';
import {
  isRuleDefAlt,
  isRuleDefChar,
  isRuleDefCharAlt,
  isRuleDefCharNot,
  isRuleDefCharRngUpper,
  isRuleDefEnd,
  isRuleDefRef,
} from '../rules-builder/type-guards.ts';
import type { InternalRuleDef } from '../rules-builder/types.ts';

export const buildRuleStack = (
  linearRules: InternalRuleDef[] | undefined
): UnresolvedRule[][] => {
  // a rule id that was never defined shows up as a hole in the rules array; treat it
  // as an empty rule.
  if (!linearRules) {
    linearRules = [];
  }

  let paths: UnresolvedRule[] = [];
  const stack: UnresolvedRule[][] = [];

  let idx = 0;
  while (idx < linearRules.length) {
    const ruleDef = linearRules[idx];
    if (isRuleDefChar(ruleDef) || isRuleDefCharNot(ruleDef)) {
      // this could be a single char, or a range, or a sequence of alts; we don't
      // know until we step through it.
      const isExclude = isRuleDefCharNot(ruleDef);
      const values: (number | Range)[] = [...ruleDef.value];
      idx += 1;
      let rule: InternalRuleDef | undefined = linearRules[idx];
      while (
        idx < linearRules.length &&
        (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))
      ) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          const prevValue = values.pop();
          if (isRange(prevValue)) {
            throw new Error(
              `Unexpected range, expected a number but got a list: ${JSON.stringify(
                prevValue
              )}`
            );
          }
          if (prevValue === undefined) {
            throw new Error('Unexpected undefined value');
          }
          values.push([prevValue, rule.value]);
        }
        if (isRuleDefCharAlt(rule)) {
          values.push(rule.value);
        }
        idx += 1;
        rule = linearRules[idx];
      }
      paths.push(isExclude ? new RuleCharExclude(values) : new RuleChar(values));
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
          `Encountered char alt, should be handled by above block: ${ruleDef.type}`
        );
      } else {
        throw new Error(`Unsupported rule type: ${ruleDef.type}`);
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
