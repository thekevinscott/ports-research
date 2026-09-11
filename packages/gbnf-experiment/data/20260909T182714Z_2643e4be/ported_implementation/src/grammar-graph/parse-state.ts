import { ValueError } from "../utils/errors/python-errors.js";
import type { ResolvedRule } from "./grammar-graph-types.js";
import type { Graph } from "./graph.js";
import type { Pointers } from "./pointers.js";

export class ParseState {
  #graph: Graph;
  #pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.#graph = graph;
    this.#pointers = pointers;
  }

  *[Symbol.iterator](): Generator<ResolvedRule> {
    yield* this.rules();
  }

  *rules(): Generator<ResolvedRule> {
    const rules: Set<string> = new Set();
    for (const pointer of this.#pointers) {
      const rule = pointer.rule as ResolvedRule;
      const key = JSON.stringify(rule.toDict());
      if (!rules.has(key)) {
        rules.add(key);
        yield rule;
      }
    }
  }

  add(text: string): ParseState {
    if (typeof text !== "string") {
      throw new ValueError("input text must be of type string");
    }
    const pointers = this.#graph.add(text, this.#pointers);
    return new ParseState(this.#graph, pointers);
  }

  get size(): number {
    return [...this.rules()].length;
  }

  get grammar(): string {
    return this.#graph.grammar;
  }

  get graph(): Graph {
    return this.#graph;
  }

  get pointers(): Pointers {
    return this.#pointers;
  }
}
