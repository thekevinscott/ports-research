import type { GraphNode } from './graph-node.js';

export class RuleRef {
  public readonly value: number;

  // An array, not a Set: the graph relies on insertion order when walking
  // referenced nodes.
  private _nodes: GraphNode[] | undefined = undefined;

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
