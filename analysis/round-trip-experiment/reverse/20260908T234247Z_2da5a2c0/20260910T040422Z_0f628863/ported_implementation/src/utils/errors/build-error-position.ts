import { codePointLength } from '../code-points.ts';

export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  // The walk stops both when it runs past the end of the array and when it hits an
  // empty line.
  while (
    lineIdx < lines.length &&
    lines[lineIdx] !== '' &&
    pos > codePointLength(lines[lineIdx]) - 1
  ) {
    pos -= codePointLength(lines[lineIdx]);
    lineIdx += 1;
  }

  const linesToShow: string[] = [];
  for (
    let i = Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1));
    i <= lineIdx;
    i++
  ) {
    // An out of range index is `undefined`, which reads as '' once joined.
    linesToShow.push(i < lines.length ? lines[i] : '');
  }

  return [...linesToShow, `${' '.repeat(pos)}^`];
};
