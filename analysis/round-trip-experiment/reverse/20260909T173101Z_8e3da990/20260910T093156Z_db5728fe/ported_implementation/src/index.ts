/**
 * A library for parsing GBNF grammars.
 *
 * ```ts
 * import GBNF from 'gbnf';
 *
 * let state = GBNF('root ::= "yes" | "no"');
 * [...state].map(rule => rule.value); // [[121], [110]]
 * state = state.add('y');
 * [...state].map(rule => rule.value); // [[101]]
 * ```
 */
import { GBNF } from './gbnf.js';

export { GBNF };
export { ParseState } from './grammar-graph/parse-state.js';
export { isRange } from './grammar-graph/type-guards.js';
export { RuleType } from './grammar-graph/types.js';
export type {
  Range,
  ResolvedRule,
  ResolvedRule as Rule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  ValidInput,
} from './grammar-graph/types.js';
export { GrammarParseError } from './utils/errors/grammar-parse-error.js';
export { InputParseError } from './utils/errors/input-parse-error.js';

export default GBNF;
