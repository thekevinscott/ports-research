import type { GraphNode } from './graphNode.js';

export class RuleRef {
  value: number;
  private _nodes?: GraphNode[];

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
