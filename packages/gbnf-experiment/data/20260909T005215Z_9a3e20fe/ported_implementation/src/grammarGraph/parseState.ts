import type { ResolvedRule } from './grammarGraphTypes.ts';
import type { Graph } from './graph.ts';
import type { Pointers } from './pointers.ts';

/**
 * An immutable snapshot of where a parse currently stands: the set of rules the
 * grammar will accept next. Feeding it more input returns a new `ParseState`.
 */
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
    const seen = new Set<string>();
    for (const pointer of this.#pointers) {
      const rule = pointer.rule as ResolvedRule;
      const key = JSON.stringify(rule.toDict());
      if (!seen.has(key)) {
        seen.add(key);
        yield rule;
      }
    }
  }

  add(text: string): ParseState {
    if (typeof text !== 'string') {
      throw new Error('input text must be of type string');
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
