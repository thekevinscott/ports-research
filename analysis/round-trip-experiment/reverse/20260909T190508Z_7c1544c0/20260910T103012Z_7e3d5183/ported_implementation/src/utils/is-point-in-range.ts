export const isPointInRange = (point: number, range: number[]): boolean => {
  const [start, end] = [range[0], range[1]];
  return start <= point && point <= end;
};
