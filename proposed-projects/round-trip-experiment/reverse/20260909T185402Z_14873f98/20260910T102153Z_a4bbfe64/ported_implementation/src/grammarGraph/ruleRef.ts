import type { GraphNode } from './graphNode';

export class RuleRef {
  private _nodes?: GraphNode[];

  constructor(public value: number) {}

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
