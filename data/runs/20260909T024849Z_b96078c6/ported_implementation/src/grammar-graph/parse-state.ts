import type { ResolvedRule } from "./grammar-graph-types.ts";
import type { Graph } from "./graph.ts";
import type { Pointers } from "./pointers.ts";

export class ParseState {
  #graph: Graph;
  #pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.#graph = graph;
    this.#pointers = pointers;
  }

  *rules(): Generator<ResolvedRule> {
    const rules = new Set<string>();
    for (const pointer of this.#pointers) {
      const rule = pointer.rule as ResolvedRule;
      const key = JSON.stringify(rule);
      if (!rules.has(key)) {
        rules.add(key);
        yield rule;
      }
    }
  }

  [Symbol.iterator](): Generator<ResolvedRule> {
    return this.rules();
  }

  add(text: string): ParseState {
    if (typeof text !== "string") {
      throw new Error("input text must be of type string");
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
}
