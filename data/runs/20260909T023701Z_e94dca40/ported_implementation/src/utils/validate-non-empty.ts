export const validateNonEmpty = <T>(value: T[]): T[] => {
  if (!value.length) {
    throw new Error('Value cannot be empty.');
  }
  return value;
};
