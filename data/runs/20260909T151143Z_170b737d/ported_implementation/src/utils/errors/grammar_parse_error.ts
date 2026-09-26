import { build_error_position } from "./build_error_position.ts";

export const GRAMMAR_PARSER_ERROR_HEADER_MESSAGE = (reason: string): string =>
  `Failed to parse grammar: ${reason}`;

export class GrammarParseError extends Error {
  grammar: string;
  pos: number;
  reason: string;

  constructor(grammar: string, pos: number, reason: string) {
    super(
      [
        GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
        "",
        ...build_error_position(grammar, pos),
      ].join("\n"),
    );
    this.name = "GrammarParseError";
    this.grammar = grammar;
    this.pos = pos;
    this.reason = reason;
  }

  toString(): string {
    return [
      GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(this.reason),
      "",
      ...build_error_position(this.grammar, this.pos),
    ].join("\n");
  }
}
