import type { GraphNode } from './graphNode.js';

/** A reference to another rule; never exposed to the end user. */
export class RuleRef {
  public readonly value: number;
  private innerNodes: GraphNode[] | null = null;

  public constructor(value: number) {
    this.value = value;
  }

  public get nodes(): GraphNode[] {
    if (this.innerNodes === null) {
      throw new Error('Nodes are not set');
    }
    return this.innerNodes;
  }

  public set nodes(nodes: GraphNode[]) {
    this.innerNodes = nodes;
  }
}
