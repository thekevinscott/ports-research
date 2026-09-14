import type { GraphNode } from './graph-node.ts';

export class RuleRef {
  #nodes: Set<GraphNode> | null = null;
  value: number;

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

  equals(other: unknown): boolean {
    return other instanceof RuleRef && this.value === other.value;
  }
}
