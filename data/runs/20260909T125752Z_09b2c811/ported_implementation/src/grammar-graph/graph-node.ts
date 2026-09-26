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
  next: GraphNode | null;
  meta: GraphNodeMeta;
  private _id: string | null = null;

  constructor(
    rule: T,
    meta: GraphNodeMeta | null,
    nextNode: GraphNode | null = null
  ) {
    this.rule = rule;
    if (!meta) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = nextNode;
  }

  get id(): string {
    if (this._id === null) {
      this._id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this._id;
  }

  print(opts: PrintOpts): string {
    return printGraphNode(this)(opts);
  }
}

export type GraphNodeRuleRef = GraphNode<RuleRef>;
