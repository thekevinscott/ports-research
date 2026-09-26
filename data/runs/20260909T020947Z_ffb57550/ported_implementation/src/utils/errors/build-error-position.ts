import { getLengthInCodePoints } from './get-input-as-string.js';

export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }
  const lines = src.split('\n');
  const srcLength = getLengthInCodePoints(src);

  let lineIdx = 0;
  while (
    lines[lineIdx] &&
    pos > getLengthInCodePoints(lines[lineIdx]) - 1 &&
    pos < srcLength
  ) {
    pos -= getLengthInCodePoints(lines[lineIdx]);
    lineIdx += 1;
  }

  const linesToShow = lines.slice(
    Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)),
    lineIdx + 1,
  );

  return [...linesToShow, `${' '.repeat(Math.max(0, pos))}^`];
};
