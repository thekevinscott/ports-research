// A stand-in implementation whose construction is keyed on the grammar; "!" in an added input raises at its position.
class InputParseError extends Error {
  constructor(public pos: number) {
    super(`rejected at ${pos}`);
  }
}

class State {
  constructor(private seen: string) {}

  *[Symbol.iterator]() {
    yield { type: "char", value: Array.from(this.seen, (c) => c.codePointAt(0)) };
    yield { type: "end" };
  }

  add(text: string): State {
    if (text.includes("!")) throw new InputParseError(text.indexOf("!"));
    return new State(this.seen + text);
  }
}

export default function GBNF(grammar: string): State {
  console.log("noise on stdout");
  if (grammar === "error") throw new TypeError("bad grammar");
  if (grammar === "hang") for (;;) {}
  if (grammar === "exit") process.exit(3);
  return new State("");
}
