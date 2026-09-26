export const parseSpace = (src: string, pos: number, newlineOk: boolean): number => {
  while (
    src[pos] === ' ' ||
    src[pos] === '\t' ||
    src[pos] === '#' ||
    (newlineOk && (src[pos] === '\r' || src[pos] === '\n'))
  ) {
    if (src[pos] === '#') {
      while (src[pos] !== undefined && src[pos] !== '\r' && src[pos] !== '\n') {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
