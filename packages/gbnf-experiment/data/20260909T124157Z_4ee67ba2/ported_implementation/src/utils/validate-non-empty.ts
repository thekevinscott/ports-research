export const validateNonEmpty = (value: number[]): number[] => {
  if (value.length === 0) {
    throw new Error('Value cannot be empty.');
  }
  return value;
};
