import type { GraphNode } from './graph-node.ts';

/**
 * A reference to another rule. Compared by identity.
 *
 * The referenced nodes are stored as an insertion-ordered, de-duplicated list so
 * that rule ordering stays deterministic.
 */
export class RuleRef {
  value: number;
  #nodes: GraphNode[] | undefined = undefined;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): GraphNode[] {
    if (this.#nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this.#nodes;
  }

  set nodes(nodes: Iterable<GraphNode>) {
    const seen: GraphNode[] = [];
    for (const node of nodes) {
      if (!seen.includes(node)) {
        seen.push(node);
      }
    }
    this.#nodes = seen;
  }

  toString(): string {
    return `RuleRef(${this.value})`;
  }
}
