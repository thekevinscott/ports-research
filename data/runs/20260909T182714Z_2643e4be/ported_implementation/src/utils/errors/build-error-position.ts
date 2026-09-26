import { IndexError } from "./python-errors.js";

const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

// Python strings are sequences of code points; positions handed to this
// function are code point offsets, so measure lengths the same way.
const codePointLength = (src: string): number => Array.from(src).length;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === "") {
    return ["No input provided"];
  }
  const lines = src.split("\n");
  const srcLength = codePointLength(src);

  let lineIdx = 0;
  // `lines[line_idx]` is evaluated first in the reference implementation, so
  // walking past the last line raises rather than ending the loop.
  for (;;) {
    if (lineIdx >= lines.length) {
      throw new IndexError("list index out of range");
    }
    if (
      !lines[lineIdx] ||
      pos <= codePointLength(lines[lineIdx]) - 1 ||
      pos >= srcLength
    ) {
      break;
    }
    pos -= codePointLength(lines[lineIdx]);
    lineIdx += 1;
  }

  const linesToShow = lines.slice(
    Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)),
    lineIdx + 1,
  );

  return [...linesToShow, `${" ".repeat(Math.max(0, pos))}^`];
};
