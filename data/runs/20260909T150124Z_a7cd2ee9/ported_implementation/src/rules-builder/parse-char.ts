import { GrammarParseError } from '../utils/errors';

const ESCAPE_CHARS: Record<string, string> = {
  t: '\t',
  r: '\r',
  n: '\n',
};

const LITERAL_ESCAPES = ['"', '[', ']', '\\'];

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
    if (next in ESCAPE_CHARS) {
      return [ESCAPE_CHARS[next].charCodeAt(0), 2];
    }
    if (LITERAL_ESCAPES.includes(next)) {
      return [next.charCodeAt(0), 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  return [src.charCodeAt(pos), 1];
};
