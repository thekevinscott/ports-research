export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

// Python's `len` counts code points, not UTF-16 units; mirror that so error
// carets land in the same column for astral-plane input.
const codePointLength = (str: string): number => Array.from(str).length;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }
  const lines = src.split('\n');
  const srcLength = codePointLength(src);

  let lineIdx = 0;
  while (
    lines[lineIdx] &&
    pos > codePointLength(lines[lineIdx]) - 1 &&
    pos < srcLength
  ) {
    pos -= codePointLength(lines[lineIdx]);
    lineIdx += 1;
  }

  const linesToShow = lines.slice(
    Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)),
    lineIdx + 1,
  );

  return [...linesToShow, `${' '.repeat(Math.max(0, pos))}^`];
};
