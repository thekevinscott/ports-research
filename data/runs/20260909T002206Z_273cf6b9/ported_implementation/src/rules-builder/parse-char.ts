import { GrammarParseError } from '../utils/errors/index.ts';

const ESCAPE_SEQUENCES: Record<string, number> = {
  t: 9,
  r: 13,
  n: 10,
};

const LITERAL_ESCAPES = ['"', '[', ']', '\\'];

/** Returns the code point at `pos`, along with the number of characters it consumed. */
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
    if (Object.hasOwn(ESCAPE_SEQUENCES, next)) {
      return [ESCAPE_SEQUENCES[next], 2];
    }
    if (LITERAL_ESCAPES.includes(next)) {
      return [next.codePointAt(0) as number, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  return [src.codePointAt(pos) as number, 1];
};
