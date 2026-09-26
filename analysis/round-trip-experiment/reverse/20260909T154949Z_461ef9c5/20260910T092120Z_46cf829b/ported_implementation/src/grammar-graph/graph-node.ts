import { colorize, Colorize } from './colorize.js';
import type { GraphPointer } from './graph-pointer.js';
import { printGraphNode } from './print.js';
import type { Pointers } from './types-internal.js';
import type { UnresolvedRule } from './types.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  rule: UnresolvedRule;
  meta: GraphNodeMeta;
  next?: GraphNode;
  private _id?: string;

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
      const { stackId, pathId, stepId } = this.meta;
      this._id = `${stackId},${pathId},${stepId}`;
    }
    return this._id;
  }

  print({ pointers, showPosition = false, col = colorize }: {
    pointers?: Pointers | GraphPointer[];
    showPosition?: boolean;
    col?: Colorize;
  } = {}): string {
    return printGraphNode(this, { pointers, showPosition, col });
  }
}
