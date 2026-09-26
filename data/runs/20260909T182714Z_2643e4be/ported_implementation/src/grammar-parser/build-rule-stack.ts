import { IndexError, ValueError } from "../utils/errors/python-errors.js";
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type UnresolvedRule,
} from "../grammar-graph/grammar-graph-types.js";
import { RuleRef } from "../grammar-graph/rule-ref.js";
import { isRange, isRuleEnd } from "../grammar-graph/type-guards.js";
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
} from "../rules-builder/rules-builder-types.js";

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

  throw new ValueError(
    `Unsupported rule type for make_char_rule: ${String(ruleDef)}`,
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
      let rule: InternalRuleDef | null =
        idx < linearRules.length ? linearRules[idx] : null;
      while (
        idx < linearRules.length &&
        (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))
      ) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          const prevValue = charRule.value.pop();
          if (isRange(prevValue)) {
            throw new ValueError(
              `Unexpected range, expected a number but got an array: ${JSON.stringify(prevValue)}`,
            );
          }
          if (prevValue === undefined || prevValue === null) {
            throw new ValueError("Unexpected undefined value");
          }

          charRule.value.push([prevValue, rule.value] as Range);
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
          throw new ValueError("Encountered alt without anything before it");
        }
        paths.push(new RuleEnd());
        stack.push(paths);
        paths = [];
      } else if (isRuleDefEnd(ruleDef)) {
        paths.push(new RuleEnd());
      } else if (isRuleDefRef(ruleDef)) {
        paths.push(new RuleRef(ruleDef.value));
      } else if (isRuleDefCharAlt(ruleDef)) {
        throw new ValueError(
          `Encountered char alt, should be handled by above block: ${String(ruleDef)}`,
        );
      } else {
        throw new ValueError(`Unsupported rule type: ${String(ruleDef)}`);
      }
      idx += 1;
    }
  }

  if (paths.length === 0) {
    // `paths[-1]` on an empty list raises in the reference implementation
    throw new IndexError("list index out of range");
  }
  if (!isRuleEnd(paths[paths.length - 1])) {
    paths.push(new RuleEnd());
  }

  stack.push(paths);
  return stack;
};
