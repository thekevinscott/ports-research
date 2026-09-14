/** Port of `gbnf/rules_builder/parse_space.py`. */

import { charAt } from './char-at.js';

const SPACE = new Set([' ', '\t', '#']);
const NEWLINE = new Set(['\r', '\n']);

export const parseSpace = (src: string, pos: number, newlineOk: boolean): number => {
  while (SPACE.has(charAt(src, pos)) || (newlineOk && NEWLINE.has(charAt(src, pos)))) {
    if (charAt(src, pos) === '#') {
      while (charAt(src, pos) && !NEWLINE.has(charAt(src, pos))) {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
