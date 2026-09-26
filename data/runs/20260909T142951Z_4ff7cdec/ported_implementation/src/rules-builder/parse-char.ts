import { GrammarParseError } from '../utils/errors/index.ts';

const ESCAPE_CHARS = new Map<string, number>([
  ['t', 9],
  ['r', 13],
  ['n', 10],
]);

const LITERAL_ESCAPE_CHARS = ['"', '[', ']', '\\'];

export const parseChar = (src: string, pos: number): [number, number] => {
  if (pos >= src.length) {
    throw new GrammarParseError(
      src,
      pos,
      'Unexpected end of grammar input, failed to complete parse'
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
    const escapeChar = ESCAPE_CHARS.get(escaped);
    if (escapeChar !== undefined) {
      return [escapeChar, 2];
    }
    if (LITERAL_ESCAPE_CHARS.includes(escaped)) {
      return [escaped.codePointAt(0) as number, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  return [src.codePointAt(pos) as number, 1];
};
