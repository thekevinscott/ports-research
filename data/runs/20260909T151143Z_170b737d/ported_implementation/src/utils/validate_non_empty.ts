export const validate_non_empty = (value: number[]): number[] => {
  if (value.length === 0) {
    throw new Error("Value cannot be empty.");
  }
  return value;
};
