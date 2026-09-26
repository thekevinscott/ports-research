import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from "../grammar-graph/grammar-graph-types.ts";
import type { Range, UnresolvedRule } from "../grammar-graph/grammar-graph-types.ts";
import { RuleRef } from "../grammar-graph/rule-ref.ts";
import { isRange, isRuleEnd } from "../grammar-graph/type-guards.ts";
import type {
  InternalRuleDef,
  InternalRuleDefChar,
  InternalRuleDefCharNot,
} from "../rules-builder/rules-builder-types.ts";
import {
  isRuleDefAlt,
  isRuleDefChar,
  isRuleDefCharAlt,
  isRuleDefCharNot,
  isRuleDefCharRngUpper,
  isRuleDefEnd,
  isRuleDefRef,
} from "../rules-builder/rules-builder-types.ts";

export const makeCharRule = (
  ruleDef: InternalRuleDefChar | InternalRuleDefCharNot,
): RuleChar | RuleCharExclude => {
  if (isRuleDefCharNot(ruleDef)) {
    return new RuleCharExclude(ruleDef.value);
  }
  if (isRuleDefChar(ruleDef)) {
    return new RuleChar(ruleDef.value);
  }

  throw new Error(`Unsupported rule type for make_char_rule: ${ruleDef}`);
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
      let rule: InternalRuleDef | undefined =
        idx < linearRules.length ? linearRules[idx] : undefined;
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
            throw new Error("Unexpected undefined value");
          }

          charRule.value.push([prevValue, rule.value] as Range);
        }
        if (isRuleDefCharAlt(rule)) {
          charRule.value.push(rule.value);
        }
        idx += 1;
        rule = idx < linearRules.length ? linearRules[idx] : undefined;
      }
      paths.push(charRule);
    } else {
      if (isRuleDefAlt(ruleDef)) {
        if (paths.length === 0) {
          throw new Error("Encountered alt without anything before it");
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
