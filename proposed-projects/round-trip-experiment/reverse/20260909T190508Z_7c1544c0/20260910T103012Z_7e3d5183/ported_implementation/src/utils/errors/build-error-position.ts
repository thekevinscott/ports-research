import { length } from '../js.js';

export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  while (
    lineIdx < lines.length &&
    lines[lineIdx] !== '' &&
    pos > length(lines[lineIdx]) - 1
  ) {
    pos -= length(lines[lineIdx]);
    lineIdx += 1;
  }

  const linesToShow: string[] = [];
  for (
    let i = Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1));
    i <= lineIdx;
    i++
  ) {
    // the line index can run past the end of the source, in which case the
    // reference implementation renders an empty line.
    linesToShow.push(i < lines.length ? lines[i] : '');
  }

  return [...linesToShow, `${' '.repeat(Math.max(pos, 0))}^`];
};
