import type { Graph, Pointers } from './graph.js';
import type { ResolvedRule, ValidInput } from './types.js';

export class ParseState {
  private graph: Graph;
  private pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.graph = graph;
    this.pointers = pointers;
  }

  *[Symbol.iterator](): IterableIterator<ResolvedRule> {
    yield* this.rules();
  }

  *rules(): Generator<ResolvedRule> {
    const rules = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule as ResolvedRule;
      const key = JSON.stringify(rule);
      if (!rules.has(key)) {
        rules.add(key);
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
    return `ParseState(${JSON.stringify([...this.rules()])})`;
  }
}
