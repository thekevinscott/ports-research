import type { ResolvedRule } from './grammar_graph_types.ts';
import type { Graph } from './graph.ts';
import type { Pointers } from './pointers.ts';

export class ParseState {
  private __graph__: Graph;
  private __pointers__: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.__graph__ = graph;
    this.__pointers__ = pointers;
  }

  *[Symbol.iterator](): Generator<ResolvedRule> {
    yield* this.rules();
  }

  *rules(): Generator<ResolvedRule> {
    const rules = new Set<string>();
    for (const pointer of this.__pointers__) {
      const rule = pointer.rule as ResolvedRule;
      const key = JSON.stringify(rule.toJSON());
      if (!rules.has(key)) {
        rules.add(key);
        yield rule;
      }
    }
  }

  add(text: string): ParseState {
    if (typeof text !== 'string') {
      throw new Error('input text must be of type string');
    }
    const pointers = this.__graph__.add(text, this.__pointers__);
    return new ParseState(this.__graph__, pointers);
  }

  get size(): number {
    return Array.from(this.rules()).length;
  }

  get grammar(): string {
    return this.__graph__.grammar;
  }

  get pointers(): Pointers {
    return this.__pointers__;
  }

  get graph(): Graph {
    return this.__graph__;
  }
}
