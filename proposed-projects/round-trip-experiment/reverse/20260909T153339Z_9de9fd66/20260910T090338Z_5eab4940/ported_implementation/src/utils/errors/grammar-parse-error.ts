import { buildErrorPosition } from './build-error-position.js';

export const GRAMMAR_PARSER_ERROR_HEADER_MESSAGE = (reason: string): string =>
  `Failed to parse grammar: ${reason}`;

export class GrammarParseError extends Error {
  override name = 'GrammarParseError';

  constructor(
    public grammar: string,
    public pos: number,
    public reason: string
  ) {
    super(
      [
        GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
        '',
        ...buildErrorPosition(grammar, pos),
      ].join('\n')
    );
  }
}
