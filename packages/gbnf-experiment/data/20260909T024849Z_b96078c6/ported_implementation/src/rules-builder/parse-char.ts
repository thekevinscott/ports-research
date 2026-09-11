import { asCodePoints, asString } from "../utils/code-points.ts";
import { GrammarParseError } from "../utils/errors/grammar-parse-error.ts";

const ESCAPED_CHARS: Record<string, number> = {
  t: 9,
  r: 13,
  n: 10,
};

const HEX_ESCAPES: Record<string, number> = {
  x: 4,
  u: 6,
  U: 10,
};

const LITERAL_ESCAPES = ['"', "[", "]", "\\"];

/**
 * Parse a single (possibly escaped) character out of `src` at `pos`.
 *
 * @returns a tuple of the character's code point and the number of code points consumed.
 */
export const parseChar = (src: string | string[], pos: number): [number, number] => {
  const chars = asCodePoints(src);

  if (pos >= chars.length) {
    throw new GrammarParseError(
      asString(src),
      pos,
      "Unexpected end of grammar input, failed to complete parse",
    );
  }

  if (chars[pos] === "\\") {
    const escaped = chars[pos + 1];

    const hexLength = HEX_ESCAPES[escaped];
    if (hexLength !== undefined) {
      const hex = chars.slice(pos + 2, pos + hexLength).join("");
      // `int(hex, 16)` in the reference rejects anything that is not entirely hex digits.
      const value = /^[0-9a-fA-F]+$/.test(hex) ? Number.parseInt(hex, 16) : Number.NaN;
      if (Number.isNaN(value)) {
        throw new GrammarParseError(
          asString(src),
          pos,
          `Invalid hex escape at ${chars[pos]}`,
        );
      }
      return [value, hexLength];
    }

    if (escaped in ESCAPED_CHARS) {
      return [ESCAPED_CHARS[escaped], 2];
    }

    if (LITERAL_ESCAPES.includes(escaped)) {
      return [escaped.codePointAt(0) as number, 2];
    }

    throw new GrammarParseError(asString(src), pos, `Unknown escape at ${chars[pos]}`);
  }

  return [chars[pos].codePointAt(0) as number, 1];
};
