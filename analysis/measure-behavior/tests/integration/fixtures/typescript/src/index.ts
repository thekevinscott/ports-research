// A stand-in implementation whose behavior is keyed on the input, one input per outcome.
class InputParseError extends Error {}

export default function GBNF(grammar: string, initialString = ""): Iterable<{ type: string }> {
  console.log("noise on stdout");
  if (initialString === "accept") return [{ type: "char" }, { type: "end" }];
  if (initialString === "prefix") return [{ type: "char" }];
  if (initialString === "reject") throw new InputParseError("rejected at 0");
  if (initialString === "error") throw new TypeError("bad grammar");
  if (initialString === "hang") for (;;) {}
  process.exit(3);
}
