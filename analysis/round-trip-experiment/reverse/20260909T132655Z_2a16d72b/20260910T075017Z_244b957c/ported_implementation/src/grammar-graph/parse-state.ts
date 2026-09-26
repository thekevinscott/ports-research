import { getSerializedRuleKey } from './get-serialized-rule-key.js';
import type { GenericSet } from './generic-set.js';
import type { Graph } from './graph.js';
import type { GraphPointer } from './graph-pointer.js';
import type { Rule } from './types.js';

export class ParseState {
  private _graph: Graph;
  private _pointers: GenericSet<GraphPointer, string>;

  constructor(graph: Graph, pointers: GenericSet<GraphPointer, string>) {
    this._graph = graph;
    this._pointers = pointers;
  }

  *[Symbol.iterator](): IterableIterator<Rule> {
    yield* this.rules();
  }

  *rules(): Generator<Rule> {
    const seen = new Set<string>();
    for (const pointer of this._pointers) {
      const rule = pointer.rule;
      const key = getSerializedRuleKey(rule);
      if (!seen.has(key)) {
        seen.add(key);
        yield rule as Rule;
      }
    }
  }

  add(input: string): ParseState {
    const pointers = this._graph.add(input, this._pointers);
    return new ParseState(this._graph, pointers);
  }

  get size(): number {
    return [...this.rules()].length;
  }

  get grammar(): string {
    return this._graph.grammar;
  }

  toString(): string {
    return `ParseState(${[...this.rules()].map((r) => `${r}`).join(', ')})`;
  }
}
