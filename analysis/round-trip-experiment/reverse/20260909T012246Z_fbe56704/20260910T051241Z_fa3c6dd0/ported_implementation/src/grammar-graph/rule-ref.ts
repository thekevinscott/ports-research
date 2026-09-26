import type { GraphNode } from './graph-node.ts';

export class RuleRef {
  value: number;
  // the referenced nodes, in insertion order.
  private _nodes: GraphNode[] | undefined;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): GraphNode[] {
    if (this._nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this._nodes;
  }

  set nodes(nodes: GraphNode[]) {
    this._nodes = nodes;
  }
}
