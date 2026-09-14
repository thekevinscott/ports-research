import type { PrintOpts, UnresolvedRule } from "./grammar_graph_types.ts";
import { print_graph_node } from "./print.ts";
import type { RuleRef } from "./rule_ref.ts";

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode<T extends UnresolvedRule = UnresolvedRule> {
  rule: T;
  next: GraphNode | null;
  meta: GraphNodeMeta;
  private __id__: string | null = null;

  constructor(rule: T, meta: GraphNodeMeta | null | undefined, next_node: GraphNode | null = null) {
    this.rule = rule;
    if (meta === null || meta === undefined) {
      throw new Error("Meta is undefined");
    }
    this.meta = meta;
    this.next = next_node;
  }

  get id(): string {
    if (this.__id__ === null) {
      this.__id__ = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.__id__;
  }

  print(opts: PrintOpts): string {
    return print_graph_node(this)(opts);
  }

  toString(): string {
    return `<GraphNode ${this.id} ${this.rule}>`;
  }
}

export type GraphNodeRuleRef = GraphNode<RuleRef>;
