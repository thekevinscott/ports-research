const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  // a falsy (empty) line halts the walk, mirroring the reference implementation
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
    if (i < lines.length) {
      linesToShow.push(lines[i]);
    }
  }

  // `' ' * pos` is empty rather than an error for a negative count in the reference
  return [...linesToShow, `${' '.repeat(Math.max(0, pos))}^`];
};
