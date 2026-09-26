import { colorize as defaultColorize } from './colorize.ts';
import type { Colorize } from './colorize.ts';
import { printGraphNode, type Pointers } from './print.ts';
import type { UnresolvedRule } from './types.ts';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  rule: UnresolvedRule;
  meta: GraphNodeMeta;
  next: GraphNode | undefined;
  private _id: string | undefined;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (!meta) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  get id(): string {
    if (!this._id) {
      this._id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this._id;
  }

  print({
    colorize = defaultColorize,
    pointers,
    showPosition = false,
  }: {
    colorize?: Colorize;
    pointers?: Pointers;
    showPosition?: boolean;
  } = {}): string {
    return printGraphNode(this, colorize, pointers, showPosition);
  }
}
