export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

// The reference can index past the end of the `lines` array; the resulting
// `undefined` is rendered as an empty string, so error messages keep an empty
// line there.
const MISSING_LINE = '';

/** `lines[idx]` with out-of-bounds indexes reading as the falsy empty string. */
const lineAt = (lines: string[], idx: number): string =>
  idx >= 0 && idx < lines.length ? lines[idx] : '';

/** A line's length in code points, matching the reference's `len()`. */
const lineLength = (line: string): number => Array.from(line).length;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  while (lineAt(lines, lineIdx) && pos > lineLength(lines[lineIdx]) - 1) {
    pos -= lineLength(lines[lineIdx]);
    lineIdx += 1;
  }

  const linesToShow: string[] = [];
  for (
    let i = Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1));
    i <= lineIdx;
    i += 1
  ) {
    linesToShow.push(i >= 0 && i < lines.length ? lines[i] : MISSING_LINE);
  }

  return [...linesToShow, `${' '.repeat(pos)}^`];
};
