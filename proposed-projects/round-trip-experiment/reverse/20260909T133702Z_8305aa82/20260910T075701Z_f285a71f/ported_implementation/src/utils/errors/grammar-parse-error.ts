import { buildErrorPosition } from './build-error-position.js';

export const GRAMMAR_PARSER_ERROR_HEADER_MESSAGE = (reason: string): string =>
  `Failed to parse grammar: ${reason}`;

export class GrammarParseError extends Error {
  public grammar: string;
  public reason: string;
  public pos: number;

  constructor(grammar: string, pos: number, reason: string) {
    const message = [
      GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
      '',
      ...buildErrorPosition(grammar, pos),
    ].join('\n');
    super(message);
    this.name = 'GrammarParseError';
    this.grammar = grammar;
    this.reason = reason;
    this.pos = pos;
    Object.setPrototypeOf(this, GrammarParseError.prototype);
  }
}
