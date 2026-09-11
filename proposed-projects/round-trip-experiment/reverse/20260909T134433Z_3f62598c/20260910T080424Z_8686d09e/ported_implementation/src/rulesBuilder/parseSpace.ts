import { charAt } from '../utils/charAt.js';

export const parseSpace = (src: string, pos: number, newlineOk: boolean): number => {
  const isSpace = (char: string): boolean => char === ' ' || char === '\t' || char === '#' ||
    (newlineOk && (char === '\r' || char === '\n'));

  while (isSpace(charAt(src, pos))) {
    if (charAt(src, pos) === '#') {
      while (charAt(src, pos) && charAt(src, pos) !== '\r' && charAt(src, pos) !== '\n') {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
