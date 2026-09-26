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
 * States are immutable; `state.add(token)` returns the next state.
 */
import { GBNF } from './gbnf.js';

export { GBNF };
export { ParseState } from './grammar-graph/parse-state.js';
export { isRange } from './grammar-graph/type-guards.js';
export {
  type Range,
  type ResolvedRule,
  type ResolvedRule as Rule,
  type RuleChar,
  type RuleCharExclude,
  type RuleEnd,
  RuleType,
  type ValidInput,
  ruleToDict,
} from './grammar-graph/types.js';
export { GrammarParseError } from './utils/errors/grammar-parse-error.js';
export { InputParseError } from './utils/errors/input-parse-error.js';

export default GBNF;
