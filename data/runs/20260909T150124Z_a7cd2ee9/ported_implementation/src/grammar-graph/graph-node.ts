import type { PrintOpts, UnresolvedRule } from './grammar-graph-types';
import { printGraphNode } from './print';
import type { RuleRef } from './rule-ref';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode<T extends UnresolvedRule = UnresolvedRule> {
  rule: T;
  next: GraphNode | undefined;
  meta: GraphNodeMeta;
  private cachedId: string | undefined = undefined;

  constructor(
    rule: T,
    meta: GraphNodeMeta | undefined,
    nextNode?: GraphNode | undefined
  ) {
    this.rule = rule;
    if (!meta) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = nextNode;
  }

  get id(): string {
    if (this.cachedId === undefined) {
      this.cachedId = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.cachedId;
  }

  print(opts: PrintOpts): string {
    return printGraphNode(this)(opts);
  }
}

export type GraphNodeRuleRef = GraphNode<RuleRef>;
