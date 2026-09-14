/**
 * A library for parsing GBNF grammars.
 *
 * TypeScript port of the Python reference implementation.
 */

import { GBNF } from './gbnf.js';

export { GBNF };
export { ParseState } from './grammar-graph/parse-state.js';
export { isRange } from './grammar-graph/type-guards.js';
export { RuleType } from './grammar-graph/types.js';
export type {
  Range,
  ResolvedRule as Rule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  ValidInput,
} from './grammar-graph/types.js';
export { GrammarParseError } from './utils/errors/grammar-parse-error.js';
export { InputParseError } from './utils/errors/input-parse-error.js';

export default GBNF;
