import { GrammarParseError } from "../utils/errors/index.ts";
import { is_word_char } from "./is_word_char.ts";

export const PARSE_NAME_ERROR = "Failed to find a valid name";

export const VALID_NAME_SEPARATORS = ["-", "_"];

export const parse_name = (grammar: string, pos: number): string => {
  let name = "";
  while (
    pos < grammar.length &&
    (is_word_char(grammar[pos]) || VALID_NAME_SEPARATORS.includes(grammar[pos]))
  ) {
    name += grammar[pos];
    pos += 1;
  }
  if (!name) {
    throw new GrammarParseError(grammar, pos, PARSE_NAME_ERROR);
  }
  return name;
};
