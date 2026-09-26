import { asCodePoints } from "../utils/code-points.ts";

export const parseSpace = (
  src: string | string[],
  pos: number,
  newlineOk: boolean,
): number => {
  const chars = asCodePoints(src);
  while (
    pos < chars.length &&
    (chars[pos] === " " ||
      chars[pos] === "\t" ||
      chars[pos] === "#" ||
      (newlineOk && (chars[pos] === "\r" || chars[pos] === "\n")))
  ) {
    if (chars[pos] === "#") {
      while (pos < chars.length && chars[pos] !== "\r" && chars[pos] !== "\n") {
        pos += 1;
      }
    } else {
      pos += 1;
    }
  }
  return pos;
};
