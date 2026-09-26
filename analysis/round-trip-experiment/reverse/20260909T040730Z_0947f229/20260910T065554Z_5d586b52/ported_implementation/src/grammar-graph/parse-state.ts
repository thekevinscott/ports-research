/**
 * Port of `gbnf/grammar_graph/parse_state.py`.
 *
 * The Python reference defines `__call__` so the state is callable; here the
 * class extends `Function` and returns a Proxy, which is the JavaScript way to
 * get the same thing.
 */

import type { Graph, Pointers } from './graph.js';
import { ResolvedRule, ValidInput, serializeRule } from './types.js';

export interface ParseState {
  (input: ValidInput): ParseState;
}

export class ParseState extends Function {
  // Not `#private`: methods are invoked through the Proxy, whose `this` is the
  // proxy rather than the target, and private fields are not forwarded.
  private graph: Graph;
  private pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    super();
    this.graph = graph;
    this.pointers = pointers;
    return new Proxy(this, {
      apply: (target, _thisArg, args: [ValidInput]) => target.add(args[0]),
    });
  }

  *[Symbol.iterator](): IterableIterator<ResolvedRule> {
    yield* this.rules();
  }

  *rules(): IterableIterator<ResolvedRule> {
    const seen = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule as ResolvedRule;
      const key = serializeRule(rule);
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
    return `ParseState([${[...this.rules()].map((rule) => JSON.stringify(rule)).join(', ')}])`;
  }
}
