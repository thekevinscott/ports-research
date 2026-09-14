/**
 * A library for parsing GBNF grammars.
 *
 *     import GBNF from 'gbnf';
 *
 *     const state = GBNF('root ::= "yes" | "no"');
 *     for (const rule of state) {
 *       console.log(rule);
 *     }
 *
 * `ParseState` objects are immutable; feed them more input with `state.add(...)`
 * to get the next state.
 */
import { GBNF } from './gbnf';

export { GBNF };
export default GBNF;

export { ParseState } from './grammar-graph/parse-state';
export { RuleChar, RuleCharExclude, RuleEnd, RuleType } from './grammar-graph/types';
export type {
  Range,
  ResolvedRule,
  Rule,
  UnresolvedRule,
  ValidInput,
} from './grammar-graph/types';
export { isRange } from './grammar-graph/type-guards';
export { GrammarParseError } from './utils/errors/grammar-parse-error';
export { InputParseError } from './utils/errors/input-parse-error';

// internals, exposed for parity with the reference implementation
export { Graph } from './grammar-graph/graph';
export { RuleRef } from './grammar-graph/rule-ref';
export { buildRuleStack } from './grammar-parser/build-rule-stack';
export { RulesBuilder } from './rules-builder/rules-builder';
export { InternalRuleType } from './rules-builder/types';
export type { InternalRuleDef } from './rules-builder/types';
