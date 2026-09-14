import { asCodePoints, asString } from "../utils/code-points.ts";
import { GrammarParseError } from "../utils/errors/grammar-parse-error.ts";
import { isWordChar } from "./is-word-char.ts";

export const PARSE_NAME_ERROR = "Failed to find a valid name";

export const VALID_NAME_SEPARATORS = ["-", "_"];

export const parseName = (grammar: string | string[], pos: number): string => {
  const chars = asCodePoints(grammar);
  let name = "";
  while (
    pos < chars.length &&
    (isWordChar(chars[pos]) || VALID_NAME_SEPARATORS.includes(chars[pos]))
  ) {
    name += chars[pos];
    pos += 1;
  }
  if (!name) {
    throw new GrammarParseError(asString(grammar), pos, PARSE_NAME_ERROR);
  }
  return name;
};
