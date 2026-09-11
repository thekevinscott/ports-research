import { printGraphNode } from './print.ts';

import type { PrintOpts, UnresolvedRule } from './grammar_graph_types.ts';
import type { RuleRef } from './rule_ref.ts';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode<T extends UnresolvedRule = UnresolvedRule> {
  rule: T;
  next: GraphNode | undefined;
  meta: GraphNodeMeta;

  private __id__: string | undefined = undefined;

  constructor(rule: T, meta: GraphNodeMeta | undefined | null, nextNode?: GraphNode) {
    this.rule = rule;
    if (meta === undefined || meta === null) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = nextNode ?? undefined;
  }

  get id(): string {
    if (this.__id__ === undefined) {
      this.__id__ = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.__id__;
  }

  print(opts: PrintOpts): string {
    return printGraphNode(this as GraphNode)(opts);
  }
}

export type GraphNodeRuleRef = GraphNode<RuleRef>;
