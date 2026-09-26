import type { GraphNode } from './graph-node.js';

export class RuleRef {
  value: number;
  private _nodes: GraphNode[] | null = null;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): GraphNode[] {
    if (this._nodes === null) {
      throw new Error('Nodes are not set');
    }
    return this._nodes;
  }

  set nodes(nodes: GraphNode[]) {
    this._nodes = nodes;
  }

  toString(): string {
    return `RuleRef(${this.value})`;
  }
}
