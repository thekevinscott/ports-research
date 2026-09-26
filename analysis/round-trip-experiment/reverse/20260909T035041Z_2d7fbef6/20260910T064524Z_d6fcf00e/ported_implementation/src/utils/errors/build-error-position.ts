export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

/**
 * Render the offending line(s) of `src` with a caret under `pos`.
 *
 * A position past the end of the input yields a trailing `undefined` entry,
 * which renders as an empty line once joined.
 */
export const buildErrorPosition = (
  src: string,
  pos: number,
): (string | undefined)[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  while (
    lineIdx < lines.length &&
    lines[lineIdx] &&
    pos > lines[lineIdx].length - 1
  ) {
    pos -= lines[lineIdx].length;
    lineIdx += 1;
  }

  const linesToShow: (string | undefined)[] = [];
  const first = Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1));
  for (let i = first; i <= lineIdx; i++) {
    linesToShow.push(lines[i]);
  }

  return [...linesToShow, `${' '.repeat(Math.max(pos, 0))}^`];
};
