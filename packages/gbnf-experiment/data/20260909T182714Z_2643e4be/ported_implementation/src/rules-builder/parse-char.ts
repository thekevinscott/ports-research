import { GrammarParseError } from "../utils/errors/grammar-parse-error.js";
import { ValueError, charAt } from "../utils/errors/python-errors.js";

const ESCAPED_CHARS: Record<string, string> = {
  t: "\t",
  r: "\r",
  n: "\n",
};

const HEX = /^[+-]?[0-9a-fA-F](?:_?[0-9a-fA-F])*$/;

// Equivalent of Python's `int(text, 16)`: leading/trailing whitespace and an
// optional sign are allowed, anything else raises.
const parseHex = (text: string): number => {
  const trimmed = text.trim();
  if (!HEX.test(trimmed)) {
    throw new ValueError(
      `invalid literal for int() with base 16: '${text}'`,
    );
  }
  return parseInt(trimmed.replace(/_/g, ""), 16);
};

export const parseChar = (src: string, pos: number): [number, number] => {
  if (pos >= src.length) {
    throw new GrammarParseError(
      src,
      pos,
      "Unexpected end of grammar input, failed to complete parse",
    );
  }

  if (charAt(src, pos) === "\\") {
    const next = charAt(src, pos + 1);
    if (next === "x") {
      return [parseHex(src.slice(pos + 2, pos + 4)), 4];
    }
    if (next === "u") {
      return [parseHex(src.slice(pos + 2, pos + 6)), 6];
    }
    if (next === "U") {
      return [parseHex(src.slice(pos + 2, pos + 10)), 10];
    }
    if (next in ESCAPED_CHARS) {
      return [ESCAPED_CHARS[next].codePointAt(0) as number, 2];
    }
    if (['"', "[", "]", "\\"].includes(next)) {
      return [next.codePointAt(0) as number, 2];
    }
    throw new GrammarParseError(
      src,
      pos,
      `Unknown escape at ${charAt(src, pos)}`,
    );
  }

  return [charAt(src, pos).codePointAt(0) as number, 1];
};
