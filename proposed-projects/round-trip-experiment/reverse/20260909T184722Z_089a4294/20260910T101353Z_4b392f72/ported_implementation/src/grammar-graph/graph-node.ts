import { colorize } from './colorize';
import type { Colorize } from './colorize';
import { printGraphNode } from './print';
import type { GraphPointer } from './graph-pointer';
import type { RuleRef } from './rule-ref';
import type { ResolvedRule } from './types';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export type GraphRule = ResolvedRule | RuleRef;

export class GraphNode {
  rule: GraphRule;
  meta: GraphNodeMeta;
  next: GraphNode | undefined;
  #id: string | undefined;

  constructor(rule: GraphRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (!meta) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  get id(): string {
    if (!this.#id) {
      this.#id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.#id;
  }

  print(col: Colorize = colorize, pointers?: Iterable<GraphPointer>, showPosition = false): string {
    return printGraphNode(this, col, pointers, showPosition);
  }

  toString(): string {
    return this.print(colorize, undefined, false);
  }
}
