import type { GraphNode } from './graphNode.ts';

/**
 * A placeholder for a rule defined elsewhere in the grammar. The graph resolves
 * every `RuleRef` to the set of nodes it points at once all stacks are built;
 * `RuleRef`s are never exposed to the end user.
 */
export class RuleRef {
  value: number;
  #nodes: Set<GraphNode> | null = null;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this.#nodes === null) {
      throw new Error('Nodes are not set');
    }
    return this.#nodes;
  }

  set nodes(nodes: Set<GraphNode>) {
    this.#nodes = nodes;
  }

  toRepr(): string {
    return `RuleRef(value=${this.value})`;
  }
}
