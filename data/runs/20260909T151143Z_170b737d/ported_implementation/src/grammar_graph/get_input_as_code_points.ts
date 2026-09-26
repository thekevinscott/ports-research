import type { ValidInput } from "./grammar_graph_types.ts";

export const get_code_point = (char: string): number => {
  const code_point = char.codePointAt(0);
  if (code_point === undefined) {
    throw new Error(`Could not get code point for character: ${char}`);
  }
  if (!Number.isInteger(code_point)) {
    throw new Error("code_point must be an integer!");
  }
  return code_point;
};

export const get_input_as_code_points = (src: ValidInput): number[] => {
  if (typeof src === "number") {
    return [src];
  }

  if (Array.isArray(src)) {
    for (const c of src) {
      if (!Number.isInteger(c)) {
        throw new Error(`code_point must be an integer for ${c} if src is a list`);
      }
    }
    return src;
  }

  if (typeof src === "string") {
    return [...src].map((s) => get_code_point(s));
  }

  throw new Error(`Invalid input type: ${typeof src}`);
};
