/**
 * A library for parsing GBNF grammars.
 *
 * ```ts
 * import GBNF from 'gbnf';
 *
 * let state = GBNF('root ::= "foo"');
 * [...state];            // [{ type: 'char', value: [102] }]
 * [...state.add('foo')]; // [{ type: 'end' }]
 * ```
 */
import { GBNF } from './gbnf.js';

export { GBNF };
export { ParseState } from './grammar-graph/parse-state.js';
export { isRange } from './grammar-graph/type-guards.js';
export {
  AbstractRule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
  type Range,
  type Rule,
  type ValidInput,
} from './grammar-graph/types.js';
export { GrammarParseError } from './utils/errors/grammar-parse-error.js';
export { InputParseError } from './utils/errors/input-parse-error.js';

export default GBNF;
