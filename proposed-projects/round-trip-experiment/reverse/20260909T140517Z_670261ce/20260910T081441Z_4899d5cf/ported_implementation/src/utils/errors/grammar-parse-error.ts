import { buildErrorPosition } from './build-error-position.js';

export const GRAMMAR_PARSER_ERROR_HEADER_MESSAGE = (reason: string): string =>
  `Failed to parse grammar: ${reason}`;

export class GrammarParseError extends Error {
  public readonly name = 'GrammarParseError';
  public readonly grammar: string;
  public readonly reason: string;
  public readonly pos: number;

  constructor(grammar: string, pos: number, reason: string) {
    super(
      [
        GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
        '',
        ...buildErrorPosition(grammar, pos),
      ].join('\n')
    );
    this.grammar = grammar;
    this.reason = reason;
    this.pos = pos;
  }
}
