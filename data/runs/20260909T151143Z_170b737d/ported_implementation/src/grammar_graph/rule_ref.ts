import type { GraphNode } from "./graph_node.ts";

export class RuleRef {
  private __nodes__: Set<GraphNode> | null = null;
  value: number;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this.__nodes__ === null) {
      throw new Error("Nodes are not set");
    }
    return this.__nodes__;
  }

  set nodes(nodes: Set<GraphNode>) {
    this.__nodes__ = nodes;
  }

  equals(other: unknown): boolean {
    return other instanceof RuleRef && this.value === other.value;
  }
}
