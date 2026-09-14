/** Out of range reads are the empty string rather than an error. */
export const charAt = (src: string, pos: number): string =>
  pos >= 0 && pos < src.length ? src[pos] : '';

export const parseSpace = (
  src: string,
  pos: number,
  newlineOk: boolean
): number => {
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
