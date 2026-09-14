import type { GraphNode } from "./graph-node.ts";

export class RuleRef {
  #nodes: Set<GraphNode> | null = null;
  value: number;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this.#nodes === null) {
      throw new Error("Nodes are not set");
    }
    return this.#nodes;
  }

  set nodes(nodes: Set<GraphNode>) {
    this.#nodes = nodes;
  }

  get type(): string {
    return "RuleRef";
  }

  toJSON(): Record<string, unknown> {
    return { type: this.type, value: this.value };
  }

  toString(): string {
    return `RuleRef(value=${this.value})`;
  }
}
