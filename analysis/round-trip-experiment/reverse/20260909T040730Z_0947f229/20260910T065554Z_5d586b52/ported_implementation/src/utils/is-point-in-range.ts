/** Port of `gbnf/utils/is_point_in_range.py`. */

export const isPointInRange = (point: number, [start, end]: readonly number[]): boolean =>
  start <= point && point <= end;
