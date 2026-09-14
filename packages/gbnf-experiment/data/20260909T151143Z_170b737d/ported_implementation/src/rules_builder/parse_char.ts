import { GrammarParseError } from "../utils/errors/index.ts";
import { at } from "../utils/python_compat.ts";

const ESCAPED_CONTROL_CHARS: Record<string, string> = {
  t: "\t",
  r: "\r",
  n: "\n",
};

const ESCAPED_LITERAL_CHARS = ['"', "[", "]", "\\"];

/** Returns a `[code point, characters consumed]` pair. */
export const parse_char = (src: string, pos: number): [number, number] => {
  if (pos >= src.length) {
    throw new GrammarParseError(
      src,
      pos,
      "Unexpected end of grammar input, failed to complete parse",
    );
  }

  if (src[pos] === "\\") {
    const escaped = at(src, pos + 1);
    if (escaped === "x") {
      return [parse_hex(src.slice(pos + 2, pos + 4)), 4];
    }
    if (escaped === "u") {
      return [parse_hex(src.slice(pos + 2, pos + 6)), 6];
    }
    if (escaped === "U") {
      return [parse_hex(src.slice(pos + 2, pos + 10)), 10];
    }
    if (escaped in ESCAPED_CONTROL_CHARS) {
      return [ESCAPED_CONTROL_CHARS[escaped].codePointAt(0) as number, 2];
    }
    if (ESCAPED_LITERAL_CHARS.includes(escaped)) {
      return [escaped.codePointAt(0) as number, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  // `codePointAt` mirrors Python's per-code-point indexing; the advance is 2
  // because JavaScript strings are indexed in UTF-16 units.
  const code_point = src.codePointAt(pos) as number;
  return [code_point, code_point > 0xffff ? 2 : 1];
};

const parse_hex = (digits: string): number => {
  const value = parseInt(digits, 16);
  if (Number.isNaN(value)) {
    throw new Error(`invalid literal for int() with base 16: '${digits}'`);
  }
  return value;
};
