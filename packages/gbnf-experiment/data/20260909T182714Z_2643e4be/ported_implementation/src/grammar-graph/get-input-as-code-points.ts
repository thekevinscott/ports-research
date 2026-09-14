import { ValueError } from "../utils/errors/python-errors.js";
import type { ValidInput } from "./grammar-graph-types.js";

export const getCodePoint = (char: string): number => {
  const codePoint = char.codePointAt(0);
  if (codePoint === undefined) {
    throw new ValueError(`Could not get code point for character: ${char}`);
  }
  if (!Number.isInteger(codePoint)) {
    throw new ValueError("code_point must be an integer!");
  }
  return codePoint;
};

export const getInputAsCodePoints = (src: ValidInput): number[] => {
  if (typeof src === "number") {
    return [src];
  }

  if (Array.isArray(src)) {
    for (const c of src) {
      if (!Number.isInteger(c)) {
        throw new ValueError(
          `code_point must be an integer for ${c} if src is a list`,
        );
      }
    }
    return src;
  }

  if (typeof src === "string") {
    // Python iterates strings by code point; `Array.from` does the same.
    return Array.from(src).map(getCodePoint);
  }

  throw new ValueError(`Invalid input type: ${typeof src}`);
};
