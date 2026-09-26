import { GrammarParseError } from '../utils/errors/index.ts';

const ESCAPE_CHARS: Record<string, number> = {
  t: 9,
  r: 13,
  n: 10,
};

const ESCAPED_LITERALS = ['"', '[', ']', '\\'];

/**
 * Parse a single character (or escape sequence) at `pos`.
 *
 * Returns the character's code point, along with the number of characters that
 * were consumed.
 */
export const parseChar = (src: string, pos: number): [number, number] => {
  if (pos >= src.length) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse',
    );
  }

  if (src[pos] === '\\') {
    const next = src[pos + 1];
    if (next === 'x') {
      return [parseInt(src.slice(pos + 2, pos + 4), 16), 4];
    }
    if (next === 'u') {
      return [parseInt(src.slice(pos + 2, pos + 6), 16), 6];
    }
    if (next === 'U') {
      return [parseInt(src.slice(pos + 2, pos + 10), 16), 10];
    }
    if (Object.hasOwn(ESCAPE_CHARS, next ?? '')) {
      return [ESCAPE_CHARS[next], 2];
    }
    if (ESCAPED_LITERALS.includes(next)) {
      return [next.charCodeAt(0), 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  const codePoint = src.codePointAt(pos) as number;
  // Characters outside of the BMP take up two UTF-16 code units.
  return [codePoint, codePoint > 0xffff ? 2 : 1];
};

export const parse_char = parseChar;
