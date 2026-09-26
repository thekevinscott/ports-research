import type { PrintOpts, UnresolvedRule } from './grammar-graph-types.js';
import { printGraphNode } from './print.js';
import type { RuleRef } from './rule-ref.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode<T extends UnresolvedRule = UnresolvedRule> {
  rule: T;
  next?: GraphNode;
  meta: GraphNodeMeta;
  private privateId?: string;

  constructor(rule: T, meta?: GraphNodeMeta, nextNode?: GraphNode) {
    this.rule = rule;
    if (meta === undefined) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = nextNode;
  }

  get id(): string {
    if (this.privateId === undefined) {
      this.privateId = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.privateId;
  }

  print(opts: PrintOpts): string {
    return printGraphNode(this)(opts);
  }
}

export type GraphNodeRuleRef = GraphNode<RuleRef>;
