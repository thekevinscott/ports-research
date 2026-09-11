export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  // `lines[lineIdx]` is falsy both past the end of the array and for empty lines,
  // which is what stops the walk.
  while (
    lineIdx < lines.length &&
    lines[lineIdx] &&
    pos > lines[lineIdx].length - 1
  ) {
    pos -= lines[lineIdx].length;
    lineIdx += 1;
  }

  const linesToShow: string[] = [];
  const start = Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1));
  for (let i = start; i <= lineIdx; i++) {
    linesToShow.push(i < lines.length ? lines[i] : '');
  }

  return [...linesToShow, `${' '.repeat(Math.max(0, pos))}^`];
};
