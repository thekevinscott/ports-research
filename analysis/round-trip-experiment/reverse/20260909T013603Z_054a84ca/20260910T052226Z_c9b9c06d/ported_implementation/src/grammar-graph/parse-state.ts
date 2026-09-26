import type { Graph } from './graph.js';
import type { Rule, ValidInput } from './types.js';
import type { Pointers } from './types-pointers.js';

/**
 * The rules that may come next, given the input consumed so far.
 *
 * Iterating a `ParseState` yields the currently valid rules; calling `add` with
 * more input returns the next `ParseState`.
 */
export class ParseState {
  private graph: Graph;
  private pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.graph = graph;
    this.pointers = pointers;
  }

  *[Symbol.iterator](): IterableIterator<Rule> {
    yield* this.rules();
  }

  *rules(): IterableIterator<Rule> {
    const seen = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule as Rule;
      const key = rule.serialize();
      if (!seen.has(key)) {
        seen.add(key);
        yield rule;
      }
    }
  }

  add(input: ValidInput): ParseState {
    const pointers = this.graph.add(input, this.pointers);
    return new ParseState(this.graph, pointers);
  }

  get size(): number {
    return [...this.rules()].length;
  }

  get grammar(): string {
    return this.graph.grammar;
  }

  toString(): string {
    return `ParseState([${[...this.rules()].map(rule => rule.serialize()).join(', ')}])`;
  }
}
