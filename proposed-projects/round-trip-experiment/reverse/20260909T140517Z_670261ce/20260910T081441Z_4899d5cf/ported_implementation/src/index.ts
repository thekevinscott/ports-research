/**
 * A library for parsing GBNF grammars.
 *
 *     import GBNF from 'gbnf';
 *
 *     const state = GBNF('root ::= "yes" | "no"');
 *     [...state]; // [{ type: 'char', value: [121] }, { type: 'char', value: [110] }]
 */

import { GBNF } from './gbnf.js';

export { GBNF };
export default GBNF;

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
