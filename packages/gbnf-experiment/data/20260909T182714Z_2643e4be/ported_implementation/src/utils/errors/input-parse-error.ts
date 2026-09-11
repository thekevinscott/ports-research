import { buildErrorPosition } from "./build-error-position.js";
import type { ValidInput } from "./errors-types.js";
import { getInputAsString } from "./get-input-as-string.js";

export const INPUT_PARSER_ERROR_HEADER_MESSAGE =
  "Failed to parse input string:";

const codePointLength = (src: string): number => Array.from(src).length;

export class InputParseError extends Error {
  override name = "InputParseError";
  mostRecentInput: ValidInput;
  pos: number;
  previousInput: ValidInput;

  constructor(
    mostRecentInput: ValidInput,
    pos: number,
    previousInput: ValidInput = "",
  ) {
    super(
      [
        INPUT_PARSER_ERROR_HEADER_MESSAGE,
        "",
        ...buildErrorPosition(
          `${getInputAsString(previousInput)}${getInputAsString(mostRecentInput)}`,
          pos + codePointLength(getInputAsString(previousInput)),
        ),
      ].join("\n"),
    );
    this.mostRecentInput = mostRecentInput;
    this.pos = pos;
    this.previousInput = previousInput;
  }

  get src(): string {
    return `${getInputAsString(this.previousInput)}${getInputAsString(this.mostRecentInput)}`;
  }

  get errorForMostRecentInput(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      "",
      ...buildErrorPosition(getInputAsString(this.mostRecentInput), this.pos),
    ].join("\n");
  }

  // Mirrors Python's `str(error)`, which returns the message on its own.
  override toString(): string {
    return [
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      "",
      ...buildErrorPosition(
        `${getInputAsString(this.previousInput)}${getInputAsString(this.mostRecentInput)}`,
        this.pos + codePointLength(getInputAsString(this.previousInput)),
      ),
    ].join("\n");
  }

  equals(other: unknown): boolean {
    return this.toString() === String(other);
  }
}
