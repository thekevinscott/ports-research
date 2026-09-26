import { build_error_position } from "./build_error_position.ts";
import type { ValidInput } from "./errors_types.ts";
import { get_input_as_string } from "./get_input_as_string.ts";

export const INPUT_PARSER_ERROR_HEADER_MESSAGE = "Failed to parse input string:";

export class InputParseError extends Error {
  most_recent_input: ValidInput;
  pos: number;
  previous_input: ValidInput;

  constructor(most_recent_input: ValidInput, pos: number, previous_input: ValidInput = "") {
    super(
      [
        INPUT_PARSER_ERROR_HEADER_MESSAGE,
        "",
        ...build_error_position(
          `${get_input_as_string(previous_input)}${get_input_as_string(most_recent_input)}`,
          pos + get_input_as_string(previous_input).length,
        ),
      ].join("\n"),
    );
    this.name = "InputParseError";
    this.most_recent_input = most_recent_input;
    this.pos = pos;
    this.previous_input = previous_input;
  }

  get src(): string {
    return `${get_input_as_string(this.previous_input)}${get_input_as_string(this.most_recent_input)}`;
  }

  get error_for_most_recent_input(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      "",
      ...build_error_position(get_input_as_string(this.most_recent_input), this.pos),
    ].join("\n");
  }

  toString(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      "",
      ...build_error_position(
        `${get_input_as_string(this.previous_input)}${get_input_as_string(this.most_recent_input)}`,
        this.pos + get_input_as_string(this.previous_input).length,
      ),
    ].join("\n");
  }
}
