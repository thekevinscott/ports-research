import { GrammarParseError } from '../utils/errors/index.js';

const ESCAPE_CHARS: Record<string, number> = {
  t: 9,
  r: 13,
  n: 10,
};

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
    if (next in ESCAPE_CHARS) {
      return [ESCAPE_CHARS[next], 2];
    }
    if (['"', '[', ']', '\\'].includes(next)) {
      return [next.codePointAt(0) as number, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  return [src.codePointAt(pos) as number, 1];
};
