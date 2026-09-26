import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';

/** The parsed code point, and how many characters of the source it took up. */
export type ParsedChar = [number, number];

export const parseChar = (src: string, pos: number): ParsedChar => {
  if (src[pos] === '\\') {
    const escaped = src[pos + 1];
    switch (escaped) {
      case 'x': return [parseInt(src.slice(pos + 2, pos + 4), 16), 4];
      case 'u': return [parseInt(src.slice(pos + 2, pos + 6), 16), 6];
      case 'U': return [parseInt(src.slice(pos + 2, pos + 10), 16), 10];
      case 't': return ['\t'.charCodeAt(0), 2];
      case 'r': return ['\r'.charCodeAt(0), 2];
      case 'n': return ['\n'.charCodeAt(0), 2];
      case '"':
      case '[':
      case ']':
        return [src.charCodeAt(pos + 1), 2];
      case '\\': {
        const codePoint = src.codePointAt(pos + 1);
        if (codePoint === undefined) {
          throw new GrammarParseError(src, pos, 'Could not get code point for character');
        }
        return [codePoint, 2];
      }
      default:
        throw new GrammarParseError(src, pos, `Unknown escape at ${src[pos]}`);
    }
  }

  if (src[pos] === undefined) {
    throw new GrammarParseError(src, pos, 'Unexpected end of grammar input, failed to complete parse');
  }
  const codePoint = src.codePointAt(pos) as number;
  // a character outside the Basic Multilingual Plane is a surrogate pair, so it
  // takes up two positions in the source but is still a single code point.
  return [codePoint, String.fromCodePoint(codePoint).length];
};
