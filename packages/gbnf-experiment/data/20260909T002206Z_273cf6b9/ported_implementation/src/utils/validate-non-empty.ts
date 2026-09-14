export const validateNonEmpty = (value: number[]): number[] => {
  if (!value.length) {
    throw new Error('Value cannot be empty.');
  }
  return value;
};
