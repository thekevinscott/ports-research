export const MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3;

export const build_error_position = (src: string, pos: number): string[] => {
  if (src === "") {
    return ["No input provided"];
  }
  const lines = src.split("\n");

  let line_idx = 0;
  while (lines[line_idx] && pos > lines[line_idx].length - 1 && pos < src.length) {
    pos -= lines[line_idx].length;
    line_idx += 1;
  }

  const lines_to_show = lines.slice(
    Math.max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)),
    line_idx + 1,
  );

  return [...lines_to_show, `${" ".repeat(Math.max(0, pos))}^`];
};
