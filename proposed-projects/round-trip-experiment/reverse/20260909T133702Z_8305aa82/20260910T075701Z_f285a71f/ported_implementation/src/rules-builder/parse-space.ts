export const parseSpace = (
  src: string,
  pos: number,
  newlineOk: boolean,
): number => {
  const at = (i: number): string => (i >= 0 && i < src.length ? src[i] : '');

  while (
    at(pos) === ' ' ||
    at(pos) === '\t' ||
    at(pos) === '#' ||
    (newlineOk && (at(pos) === '\r' || at(pos) === '\n'))
  ) {
    if (at(pos) === '#') {
      while (at(pos) && at(pos) !== '\r' && at(pos) !== '\n') {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
