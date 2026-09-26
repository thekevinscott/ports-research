export const parseSpace = (src: string, pos: number, newlineOk: boolean): number => {
  const at = (i: number): string | undefined =>
    i >= 0 && i < src.length ? src[i] : undefined;

  while (
    at(pos) === ' ' ||
    at(pos) === '\t' ||
    at(pos) === '#' ||
    (newlineOk && (at(pos) === '\r' || at(pos) === '\n'))
  ) {
    if (at(pos) === '#') {
      while (at(pos) !== undefined && at(pos) !== '\r' && at(pos) !== '\n') {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
