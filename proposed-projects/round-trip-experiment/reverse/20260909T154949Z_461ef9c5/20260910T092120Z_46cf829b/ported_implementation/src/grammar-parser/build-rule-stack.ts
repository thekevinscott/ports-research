import { RuleRef } from '../grammar-graph/rule-ref.js';
import { isRange, isRuleEnd } from '../grammar-graph/type-guards.js';
import {
  RuleChar,
  RuleCharExclude,
  RuleType,
  UnresolvedRule,
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
import { InternalRuleDef, InternalRuleDefChar } from '../rules-builder/types.js';

const makeCharRule = (ruleDef: InternalRuleDefChar): RuleChar | RuleCharExclude => ({
  type: isRuleDefCharNot(ruleDef) ? RuleType.CHAR_EXCLUDE : RuleType.CHAR,
  value: [...ruleDef.value],
}) as RuleChar | RuleCharExclude;

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
      let rule = linearRules[idx];
      while (idx < linearRules.length && (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          const prevValue = charRule.value.pop();
          if (prevValue === undefined) {
            throw new Error('Unexpected undefined value');
          }
          if (isRange(prevValue)) {
            throw new Error(
              `Unexpected range, expected a number but got an array: ${JSON.stringify(prevValue)}`,
            );
          }
          charRule.value.push([prevValue, rule.value]);
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
        if (paths.length === 0) {
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
          `Encountered char alt, should be handled by above block: ${ruleDef.type}`,
        );
      } else {
        throw new Error(`Unsupported rule type: ${(ruleDef as InternalRuleDef).type}`);
      }
      idx += 1;
    }
  }

  if (paths.length === 0 || !isRuleEnd(paths[paths.length - 1])) {
    paths.push({ type: RuleType.END });
  }

  stack.push(paths);

  return stack;
};
