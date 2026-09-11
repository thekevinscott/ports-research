import { GrammarParseError } from '../utils/errors/index.js';

const ESCAPE_CHARACTERS: Record<string, string> = {
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
      'Unexpected end of grammar input, failed to complete parse',
    );
  }

  if (src[pos] === '\\') {
    const escaped = src[pos + 1];
    if (escaped === 'x') {
      return [parseInt(src.slice(pos + 2, pos + 4), 16), 4];
    }
    if (escaped === 'u') {
      return [parseInt(src.slice(pos + 2, pos + 6), 16), 6];
    }
    if (escaped === 'U') {
      return [parseInt(src.slice(pos + 2, pos + 10), 16), 10];
    }
    if (Object.hasOwn(ESCAPE_CHARACTERS, escaped ?? '')) {
      return [ESCAPE_CHARACTERS[escaped].charCodeAt(0), 2];
    }
    if (LITERAL_ESCAPES.includes(escaped)) {
      return [escaped.charCodeAt(0), 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  return [src.charCodeAt(pos), 1];
};
