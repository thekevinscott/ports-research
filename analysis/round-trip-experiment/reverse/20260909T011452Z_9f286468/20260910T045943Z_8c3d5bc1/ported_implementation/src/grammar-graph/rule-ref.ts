import type { GraphNode } from './graph-node';

export class RuleRef {
  public value: number;
  private _nodes?: Set<GraphNode>;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this._nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this._nodes;
  }

  set nodes(nodes: Set<GraphNode>) {
    this._nodes = nodes;
  }
}
