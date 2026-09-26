import { RuleRef } from '../grammar-graph/rule-ref';
import { isRange, isRuleEnd } from '../grammar-graph/type-guards';
import { RuleChar, RuleCharExclude, RuleEnd } from '../grammar-graph/types';
import {
  isRuleDefAlt,
  isRuleDefChar,
  isRuleDefCharAlt,
  isRuleDefCharNot,
  isRuleDefCharRngUpper,
  isRuleDefEnd,
  isRuleDefRef,
} from '../rules-builder/type-guards';
import type { InternalRuleDef } from '../rules-builder/types';

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

const makeCharRule = (ruleDef: InternalRuleDef): RuleChar | RuleCharExclude => {
  const Cls = isRuleDefCharNot(ruleDef) ? RuleCharExclude : RuleChar;
  return new Cls([...(ruleDef.value as number[])]);
};

export const buildRuleStack = (
  linearRules?: InternalRuleDef[],
): UnresolvedRule[][] | undefined => {
  if (linearRules === undefined) {
    // the reference implementation's rules array can be sparse; holes map through
    // untouched.
    return undefined;
  }

  let paths: UnresolvedRule[] = [];
  const stack: UnresolvedRule[][] = [];

  let idx = 0;
  while (idx < linearRules.length) {
    const ruleDef = linearRules[idx];
    if (isRuleDefChar(ruleDef) || isRuleDefCharNot(ruleDef)) {
      // this could be a single char, or a range, or a sequence of alts; we don't know
      // until we step through it.
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

  if (!paths.length || !isRuleEnd(paths[paths.length - 1])) {
    paths.push(new RuleEnd());
  }

  stack.push(paths);

  return stack;
};
