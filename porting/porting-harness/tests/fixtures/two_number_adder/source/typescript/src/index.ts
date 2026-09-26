export const add = (a: number, b: number): number => {
  if (!Number.isFinite(a) || !Number.isFinite(b)) {
    throw new TypeError('add expects two finite numbers');
  }
  return a + b;
};
