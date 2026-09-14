import { buildErrorPosition } from './build-error-position.js';

export const GRAMMAR_PARSER_ERROR_HEADER_MESSAGE = (reason: string): string =>
  `Failed to parse grammar: ${reason}`;

const buildMessage = (grammar: string, pos: number, reason: string): string =>
  [
    GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
    '',
    ...buildErrorPosition(grammar, pos),
  ].join('\n');

export class GrammarParseError extends Error {
  readonly grammar: string;
  readonly pos: number;
  readonly reason: string;

  constructor(grammar: string, pos: number, reason: string) {
    super(buildMessage(grammar, pos, reason));
    // Restore the prototype chain, which is severed when subclassing built-ins
    // if this ever gets down-levelled to ES5.
    Object.setPrototypeOf(this, GrammarParseError.prototype);
    this.name = 'GrammarParseError';
    this.grammar = grammar;
    this.pos = pos;
    this.reason = reason;
  }
}
