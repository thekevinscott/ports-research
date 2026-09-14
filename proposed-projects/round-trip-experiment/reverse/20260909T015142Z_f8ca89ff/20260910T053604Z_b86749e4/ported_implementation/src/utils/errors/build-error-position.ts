export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  // `lines[lineIdx]` is falsy both when out of range and when the line is empty.
  while (lines[lineIdx] && pos > lines[lineIdx].length - 1) {
    pos -= lines[lineIdx].length;
    lineIdx += 1;
  }

  const linesToShow: string[] = [];
  for (
    let i = Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1));
    i <= lineIdx;
    i++
  ) {
    // Past the end of the grammar there is nothing to show.
    linesToShow.push(lines[i] ?? '');
  }

  return [...linesToShow, `${' '.repeat(Math.max(0, pos))}^`];
};
