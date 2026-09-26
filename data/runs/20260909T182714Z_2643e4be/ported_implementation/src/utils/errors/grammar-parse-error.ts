import { buildErrorPosition } from "./build-error-position.js";

export const GRAMMAR_PARSER_ERROR_HEADER_MESSAGE = (reason: string): string =>
  `Failed to parse grammar: ${reason}`;

export class GrammarParseError extends Error {
  override name = "GrammarParseError";
  grammar: string;
  pos: number;
  reason: string;

  constructor(grammar: string, pos: number, reason: string) {
    super(
      [
        GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
        "",
        ...buildErrorPosition(grammar, pos),
      ].join("\n"),
    );
    this.grammar = grammar;
    this.pos = pos;
    this.reason = reason;
  }

  // Mirrors Python's `str(error)`, which returns the message on its own.
  override toString(): string {
    return [
      GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(this.reason),
      "",
      ...buildErrorPosition(this.grammar, this.pos),
    ].join("\n");
  }

  equals(other: unknown): boolean {
    return this.toString() === String(other);
  }
}
