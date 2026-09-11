export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }
  const lines = src.split('\n');

  let lineIdx = 0;
  let cursor = pos;
  while (lines[lineIdx] && cursor > lines[lineIdx].length - 1 && cursor < src.length) {
    cursor -= lines[lineIdx].length;
    lineIdx += 1;
  }

  const linesToShow = lines.slice(
    Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)),
    lineIdx + 1,
  );

  return [...linesToShow, `${' '.repeat(Math.max(0, cursor))}^`];
};
