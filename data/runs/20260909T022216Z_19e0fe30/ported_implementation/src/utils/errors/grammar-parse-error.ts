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
  grammar: string;
  pos: number;
  reason: string;

  constructor(grammar: string, pos: number, reason: string) {
    super(buildMessage(grammar, pos, reason));
    Object.setPrototypeOf(this, GrammarParseError.prototype);
    this.name = 'GrammarParseError';
    this.grammar = grammar;
    this.pos = pos;
    this.reason = reason;
  }

  toString(): string {
    return buildMessage(this.grammar, this.pos, this.reason);
  }

  equals(other: unknown): boolean {
    return String(this) === String(other);
  }
}
