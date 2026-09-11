import { Colorize, colorize as defaultColorize } from './colorize.js';
import { printGraphNode } from './print.js';
import type { GenericSet } from './generic-set.js';
import type { GraphPointer } from './graph-pointer.js';
import type { RuleRef } from './rule-ref.js';
import type { Rule } from './types.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  rule: Rule | RuleRef;
  meta: GraphNodeMeta;
  next?: GraphNode;
  private _id?: string;

  constructor(rule: Rule | RuleRef, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (meta === undefined || meta === null) {
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

  print(
    pointers?: GenericSet<GraphPointer, string>,
    showPosition = false,
    colorize: Colorize = defaultColorize
  ): string {
    return printGraphNode(this, colorize, pointers, showPosition);
  }

  toString(): string {
    return this.print(undefined, false, (v) => `${v}`);
  }
}
