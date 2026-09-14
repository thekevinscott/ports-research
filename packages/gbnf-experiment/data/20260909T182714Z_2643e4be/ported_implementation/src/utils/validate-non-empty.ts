import { ValueError } from "./errors/python-errors.js";

export const validateNonEmpty = <T>(value: T[]): T[] => {
  if (value.length === 0) {
    throw new ValueError("Value cannot be empty.");
  }
  return value;
};
