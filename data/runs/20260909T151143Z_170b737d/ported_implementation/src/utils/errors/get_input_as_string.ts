import type { ValidInput } from "./errors_types.ts";

export const get_input_as_string = (src: ValidInput): string => {
  if (typeof src === "string") {
    return src;
  }
  if (typeof src === "number") {
    return String.fromCodePoint(src);
  }
  return src.map((cp) => String.fromCodePoint(cp)).join("");
};
