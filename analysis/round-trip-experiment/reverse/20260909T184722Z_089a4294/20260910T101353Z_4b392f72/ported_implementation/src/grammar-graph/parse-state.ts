import type { GenericSet } from './generic-set';
import type { Graph } from './graph';
import type { GraphPointer } from './graph-pointer';
import type { ResolvedRule, ValidInput } from './types';

export class ParseState {
  #graph: Graph;
  #pointers: GenericSet<GraphPointer, string>;

  constructor(graph: Graph, pointers: GenericSet<GraphPointer, string>) {
    this.#graph = graph;
    this.#pointers = pointers;
  }

  *[Symbol.iterator](): Generator<ResolvedRule> {
    yield* this.rules();
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

  add(input: ValidInput): ParseState {
    const pointers = this.#graph.add(input, this.#pointers);
    return new ParseState(this.#graph, pointers);
  }

  get size(): number {
    return [...this.rules()].length;
  }

  get grammar(): string {
    return this.#graph.grammar;
  }

  toString(): string {
    return `ParseState(${JSON.stringify([...this.rules()])})`;
  }
}
