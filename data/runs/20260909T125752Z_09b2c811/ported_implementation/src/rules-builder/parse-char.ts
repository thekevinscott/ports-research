import { GrammarParseError } from '../utils/errors/index.js';

const ESCAPED_CONTROL_CHARS: Record<string, number> = {
  t: 9,
  r: 13,
  n: 10,
};

const ESCAPED_LITERAL_CHARS = ['"', '[', ']', '\\'];

export const parseChar = (src: string, pos: number): [number, number] => {
  if (pos >= src.length) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse'
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
    if (next in ESCAPED_CONTROL_CHARS) {
      return [ESCAPED_CONTROL_CHARS[next], 2];
    }
    if (ESCAPED_LITERAL_CHARS.includes(next)) {
      return [next.codePointAt(0) as number, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  return [src.codePointAt(pos) as number, 1];
};
