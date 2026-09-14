import { itemAt } from '../char-at';

export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const buildErrorPosition = (src: string, pos: number): string[] => {
  if (src === '') {
    return ['No input provided'];
  }

  const lines = src.split('\n');

  let lineIdx = 0;
  while (itemAt(lines, lineIdx) && pos > lines[lineIdx].length - 1) {
    pos -= lines[lineIdx].length;
    lineIdx += 1;
  }

  const linesToShow: string[] = [];
  const start = Math.max(0, lineIdx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1));
  for (let i = start; i <= lineIdx; i++) {
    const line = itemAt(lines, i);
    linesToShow.push(line === undefined ? '' : line);
  }
  return [
    ...linesToShow,
    `${' '.repeat(Math.max(0, pos))}^`,
  ];
};
