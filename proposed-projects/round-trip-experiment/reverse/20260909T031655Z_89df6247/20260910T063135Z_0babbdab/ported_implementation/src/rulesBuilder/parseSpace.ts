const at = (src: string, pos: number): string =>
  pos >= 0 && pos < src.length ? src[pos] : '';

export const parseSpace = (
  src: string,
  pos: number,
  newlineOk: boolean
): number => {
  while (
    [' ', '\t', '#'].includes(at(src, pos)) ||
    (newlineOk && ['\r', '\n'].includes(at(src, pos)))
  ) {
    if (at(src, pos) === '#') {
      while (at(src, pos) && !['\r', '\n'].includes(at(src, pos))) {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
