import { charAt } from '../utils/js.js';

const isSpace = (char: string, newlineOk: boolean): boolean =>
  char === ' ' ||
  char === '\t' ||
  char === '#' ||
  (newlineOk && (char === '\r' || char === '\n'));

export const parseSpace = (src: string, pos: number, newlineOk: boolean): number => {
  while (isSpace(charAt(src, pos), newlineOk)) {
    if (charAt(src, pos) === '#') {
      let char = charAt(src, pos);
      while (char && char !== '\r' && char !== '\n') {
        pos += 1;
        char = charAt(src, pos);
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
