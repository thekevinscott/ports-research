import type { ResolvedRule } from './grammar-graph-types.js';
import type { Graph } from './graph.js';
import type { Pointers } from './pointers.js';

export class ParseState {
  readonly #graph: Graph;
  readonly #pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.#graph = graph;
    this.#pointers = pointers;
  }

  *rules(): Generator<ResolvedRule> {
    const seen = new Set<string>();
    for (const pointer of this.#pointers) {
      const rule = pointer.rule as ResolvedRule;
      const key = JSON.stringify(rule);
      if (!seen.has(key)) {
        seen.add(key);
        yield rule;
      }
    }
  }

  [Symbol.iterator](): Generator<ResolvedRule> {
    return this.rules();
  }

  add(text: string): ParseState {
    if (typeof text !== 'string') {
      throw new Error('input text must be of type string');
    }
    return new ParseState(this.#graph, this.#graph.add(text, this.#pointers));
  }

  get size(): number {
    return [...this.rules()].length;
  }

  get grammar(): string {
    return this.#graph.grammar;
  }
}
