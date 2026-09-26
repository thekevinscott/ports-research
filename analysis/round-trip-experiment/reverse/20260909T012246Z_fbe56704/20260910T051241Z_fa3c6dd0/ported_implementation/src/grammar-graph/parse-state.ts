import type { Graph, Pointers } from './graph.ts';
import type { ResolvedRule, ValidInput } from './types.ts';

export class ParseState {
  private _graph: Graph;
  private _pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this._graph = graph;
    this._pointers = pointers;
  }

  *[Symbol.iterator](): IterableIterator<ResolvedRule> {
    yield* this.rules();
  }

  *rules(): IterableIterator<ResolvedRule> {
    const seen = new Set<ResolvedRule>();
    for (const pointer of this._pointers) {
      const rule = pointer.rule as ResolvedRule;
      if (!seen.has(rule)) {
        seen.add(rule);
        yield rule;
      }
    }
  }

  add(input: ValidInput): ParseState {
    const pointers = this._graph.add(input, this._pointers);
    return new ParseState(this._graph, pointers);
  }

  get size(): number {
    return [...this.rules()].length;
  }

  get grammar(): string {
    return this._graph.grammar;
  }
}
