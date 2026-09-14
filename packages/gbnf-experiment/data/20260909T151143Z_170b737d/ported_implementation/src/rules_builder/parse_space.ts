export const parse_space = (src: string, pos: number, newline_ok: boolean): number => {
  while (
    pos < src.length &&
    (src[pos] === " " ||
      src[pos] === "\t" ||
      src[pos] === "#" ||
      (newline_ok && (src[pos] === "\r" || src[pos] === "\n")))
  ) {
    if (src[pos] === "#") {
      while (pos < src.length && src[pos] !== "\r" && src[pos] !== "\n") {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
