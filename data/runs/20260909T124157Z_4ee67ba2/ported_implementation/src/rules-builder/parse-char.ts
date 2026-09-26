import { GrammarParseError } from '../utils/errors/index.ts';

const HEX = /^[0-9a-fA-F]+$/;

/** Mirrors Python's `int(value, 16)`: the whole slice must be a hex literal. */
const parseHex = (src: string, pos: number, value: string): number => {
  if (!HEX.test(value)) {
    throw new GrammarParseError(src, pos, `Invalid hex escape: ${value}`);
  }
  return parseInt(value, 16);
};

const ESCAPE_CHARS: Record<string, number> = {
  t: 0x09,
  r: 0x0d,
  n: 0x0a,
};

const LITERAL_ESCAPE_CHARS = ['"', '[', ']', '\\'];

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
      return [parseHex(src, pos, src.slice(pos + 2, pos + 4)), 4];
    }
    if (next === 'u') {
      return [parseHex(src, pos, src.slice(pos + 2, pos + 6)), 6];
    }
    if (next === 'U') {
      return [parseHex(src, pos, src.slice(pos + 2, pos + 10)), 10];
    }
    if (next in ESCAPE_CHARS) {
      return [ESCAPE_CHARS[next], 2];
    }
    if (LITERAL_ESCAPE_CHARS.includes(next)) {
      return [next.codePointAt(0) as number, 2];
    }
    throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
  }

  return [src.codePointAt(pos) as number, 1];
};
