export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  // an empty line terminates the walk, matching a falsiness check on the line
  while (lineIdx < lines.length && lines[lineIdx] && pos > lines[lineIdx].length - 1) {
    pos -= lines[lineIdx].length;
    lineIdx += 1;
  }

  const linesToShow: string[] = [];
  const start = Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1));
  for (let i = start; i <= lineIdx; i++) {
    // when the position runs past the end of the input, the walk above stops on
    // a line that does not exist; it is rendered as a blank line
    linesToShow.push(i < lines.length ? lines[i] : '');
  }

  return [
    ...linesToShow,
    `${' '.repeat(Math.max(0, pos))}^`,
  ];
};
