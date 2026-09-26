import type { Graph, Pointers } from './graph';
import type { Rule, ValidInput } from './types';

export class ParseState {
  private graph: Graph;
  private pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.graph = graph;
    this.pointers = pointers;
  }

  *rules(): IterableIterator<Rule> {
    const seen = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule as Rule;
      const key = JSON.stringify([rule.type, (rule as { value?: unknown }).value]);
      if (!seen.has(key)) {
        seen.add(key);
        yield rule;
      }
    }
  }

  [Symbol.iterator](): IterableIterator<Rule> {
    return this.rules();
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
