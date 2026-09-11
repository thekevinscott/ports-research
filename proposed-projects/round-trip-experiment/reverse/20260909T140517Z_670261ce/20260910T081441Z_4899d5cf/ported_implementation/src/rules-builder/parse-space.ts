import { charAt, type Chars } from '../utils/js.js';

const SPACE = [' ', '\t', '#'];
const NEWLINE = ['\r', '\n'];

export const parseSpace = (src: Chars, pos: number, newlineOk: boolean): number => {
  while (
    SPACE.includes(charAt(src, pos)) ||
    (newlineOk && NEWLINE.includes(charAt(src, pos)))
  ) {
    if (charAt(src, pos) === '#') {
      while (charAt(src, pos) && !NEWLINE.includes(charAt(src, pos))) {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
