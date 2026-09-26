import type { GraphNode } from './graph-node.js';

export class RuleRef {
  private _nodes: Set<GraphNode> | null = null;
  value: number;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this._nodes === null) {
      throw new Error('Nodes are not set');
    }
    return this._nodes;
  }

  set nodes(nodes: Set<GraphNode>) {
    this._nodes = nodes;
  }

  equals(other: unknown): boolean {
    return other instanceof RuleRef && this.value === other.value;
  }
}
