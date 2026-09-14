import { RuleRef } from '../grammar-graph/rule-ref.js';
import { isRange, isRuleEnd } from '../grammar-graph/type-guards.js';
import {
  RuleType,
  type Range,
  type RuleChar,
  type RuleCharExclude,
  type UnresolvedRule,
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
import type {
  InternalRuleDef,
  InternalRuleDefChar,
  InternalRuleDefCharNot,
} from '../rules-builder/types.js';

const makeCharRule = (
  ruleDef: InternalRuleDefChar | InternalRuleDefCharNot
): RuleChar | RuleCharExclude =>
  isRuleDefCharNot(ruleDef)
    ? { type: RuleType.CHAR_EXCLUDE, value: [...ruleDef.value] }
    : { type: RuleType.CHAR, value: [...ruleDef.value] };

export const buildRuleStack = (
  linearRules: InternalRuleDef[]
): UnresolvedRule[][] => {
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
      while (
        idx < linearRules.length &&
        (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))
      ) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          if (!charRule.value.length) {
            throw new Error('Unexpected undefined value');
          }
          const prevValue = charRule.value.pop() as number | Range;
          if (isRange(prevValue)) {
            throw new Error(
              `Unexpected range, expected a number but got an array: ${JSON.stringify(prevValue)}`
            );
          }
          const range: Range = [prevValue, rule.value];
          charRule.value.push(range);
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
        paths.push({ type: RuleType.END });
        stack.push(paths);
        paths = [];
      } else if (isRuleDefEnd(ruleDef)) {
        paths.push({ type: RuleType.END });
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
    paths.push({ type: RuleType.END });
  }

  stack.push(paths);

  return stack;
};
