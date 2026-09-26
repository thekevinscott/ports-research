import type { PrintOpts, UnresolvedRule } from './grammar-graph-types.ts';
import { printGraphNode } from './print.ts';
import type { RuleRef } from './rule-ref.ts';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode<T extends UnresolvedRule = UnresolvedRule> {
  rule: T;
  next: GraphNode | null;
  meta: GraphNodeMeta;
  #id: string | null = null;

  constructor(rule: T, meta: GraphNodeMeta | null, nextNode: GraphNode | null = null) {
    this.rule = rule;
    if (meta === null || meta === undefined) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = nextNode;
  }

  get id(): string {
    if (this.#id === null) {
      this.#id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.#id;
  }

  print(opts: PrintOpts): string {
    return printGraphNode(this)(opts);
  }

  toString(): string {
    return `<GraphNode ${this.id} ${this.rule}>`;
  }
}

export type GraphNodeRuleRef = GraphNode<RuleRef>;
