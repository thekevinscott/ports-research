import { codePointLength, toCodePoints } from "../code-points.ts";

export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === "") {
    return ["No input provided"];
  }
  const lines = src.split("\n").map(toCodePoints);
  const srcLength = codePointLength(src);

  let lineIdx = 0;
  while (
    lines[lineIdx] !== undefined &&
    lines[lineIdx].length > 0 &&
    pos > lines[lineIdx].length - 1 &&
    pos < srcLength
  ) {
    pos -= lines[lineIdx].length;
    lineIdx += 1;
  }

  const linesToShow = lines
    .slice(Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)), lineIdx + 1)
    .map((line) => line.join(""));

  return [...linesToShow, `${" ".repeat(Math.max(0, pos))}^`];
};
