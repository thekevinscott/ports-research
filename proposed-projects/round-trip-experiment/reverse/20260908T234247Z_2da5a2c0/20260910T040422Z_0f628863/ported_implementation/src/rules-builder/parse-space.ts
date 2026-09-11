import { at } from '../utils/code-points.ts';

export const parseSpace = (src: string[], pos: number, newlineOk: boolean): number => {
  let char = at(src, pos);
  while (
    char === ' ' ||
    char === '\t' ||
    char === '#' ||
    (newlineOk && (char === '\r' || char === '\n'))
  ) {
    if (char === '#') {
      while (at(src, pos) && at(src, pos) !== '\r' && at(src, pos) !== '\n') {
        pos += 1;
      }
    } else {
      pos += 1;
    }
    char = at(src, pos);
  }
  return pos;
};
