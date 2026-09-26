import { charAt } from './char-at.ts';

export const parseSpace = (src: string, pos: number, newlineOk: boolean): number => {
  while (
    [' ', '\t', '#'].includes(charAt(src, pos)) ||
    (newlineOk && ['\r', '\n'].includes(charAt(src, pos)))
  ) {
    if (charAt(src, pos) === '#') {
      while (charAt(src, pos) && !['\r', '\n'].includes(charAt(src, pos))) {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
