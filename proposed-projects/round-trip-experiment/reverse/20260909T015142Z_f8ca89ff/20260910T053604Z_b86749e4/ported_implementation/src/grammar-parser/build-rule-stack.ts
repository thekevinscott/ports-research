import { RuleRef } from '../grammar-graph/rule-ref';
import { isRange, isRuleEnd } from '../grammar-graph/type-guards';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  UnresolvedRule,
} from '../grammar-graph/types';
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

export const makeCharRule = (
  ruleDef: InternalRuleDef
): RuleChar | RuleCharExclude => {
  if (isRuleDefCharNot(ruleDef)) {
    return new RuleCharExclude([...ruleDef.value]);
  }
  if (!isRuleDefChar(ruleDef)) {
    throw new Error(`Unsupported rule type: ${ruleDef.type}`);
  }
  return new RuleChar([...ruleDef.value]);
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
      let rule: InternalRuleDef | undefined = linearRules[idx];
      while (idx < linearRules.length && (isRuleDefCharRngUpper(rule) || isRuleDefCharAlt(rule))) {
        if (isRuleDefCharRngUpper(rule)) {
          // previous rule value should be a number
          const prevValue = charRule.value.pop();
          if (isRange(prevValue)) {
            throw new Error(
              `Unexpected range, expected a number but got an array: ${JSON.stringify(prevValue)}`
            );
          }
          if (prevValue === undefined) {
            throw new Error('Unexpected undefined value');
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
        throw new Error(`Unsupported rule type: ${(ruleDef as InternalRuleDef).type}`);
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
