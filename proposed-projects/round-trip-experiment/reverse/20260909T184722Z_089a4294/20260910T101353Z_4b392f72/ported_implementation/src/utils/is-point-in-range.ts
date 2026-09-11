export const isPointInRange = (point: number, rng: readonly number[]): boolean => {
  const [start, end] = [rng[0], rng[1]];
  return start <= point && point <= end;
};
