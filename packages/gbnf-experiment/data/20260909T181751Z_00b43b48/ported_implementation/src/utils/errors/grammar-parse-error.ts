import { buildErrorPosition } from './build-error-position.js';

export const GRAMMAR_PARSER_ERROR_HEADER_MESSAGE = (reason: string): string =>
  `Failed to parse grammar: ${reason}`;

export class GrammarParseError extends Error {
  grammar: string;
  pos: number;
  reason: string;

  constructor(grammar: string, pos: number, reason: string) {
    super([
      GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
      '',
      ...buildErrorPosition(grammar, pos),
    ].join('\n'));
    this.name = 'GrammarParseError';
    this.grammar = grammar;
    this.pos = pos;
    this.reason = reason;
    Object.setPrototypeOf(this, GrammarParseError.prototype);
  }
}
