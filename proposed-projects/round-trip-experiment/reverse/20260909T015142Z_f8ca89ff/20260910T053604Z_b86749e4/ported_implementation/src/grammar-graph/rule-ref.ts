import type { GraphNode } from './graph-node';

export class RuleRef {
  public value: number;
  private _nodes?: GraphNode[];

  constructor(value: number) {
    this.value = value;
  }

  public get nodes(): GraphNode[] {
    if (this._nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this._nodes;
  }

  public set nodes(nodes: Iterable<GraphNode>) {
    // Deduped, but insertion order is preserved: walking referenced nodes relies on it.
    this._nodes = [...new Set(nodes)];
  }
}
