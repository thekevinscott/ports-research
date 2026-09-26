/** Port of `gbnf/utils/errors/build_error_position.py`. */

export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  // An empty line is falsy, which terminates the loop early.
  while (lineIdx < lines.length && lines[lineIdx] && pos > lines[lineIdx].length - 1) {
    pos -= lines[lineIdx].length;
    lineIdx += 1;
  }

  const linesToShow: string[] = [];
  for (
    let i = Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1));
    i <= lineIdx;
    i += 1
  ) {
    // `lineIdx` can run one past the end when `pos` overshoots the source,
    // which renders as an empty line.
    linesToShow.push(i < lines.length ? lines[i] : '');
  }
  return [...linesToShow, `${' '.repeat(Math.max(0, pos))}^`];
};
