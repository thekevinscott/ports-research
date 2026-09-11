export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }
  const lines = src.split('\n');

  let lineIdx = 0;
  let line = lines[lineIdx];
  while (line && pos > line.length - 1 && pos < src.length) {
    pos -= line.length;
    lineIdx += 1;
    line = lines[lineIdx];
  }

  const linesToShow = lines.slice(
    Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)),
    lineIdx + 1,
  );

  return [...linesToShow, `${' '.repeat(Math.max(0, pos))}^`];
};
