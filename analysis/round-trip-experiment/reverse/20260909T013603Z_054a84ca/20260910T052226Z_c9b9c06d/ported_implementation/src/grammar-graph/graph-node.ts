import { colorize as defaultColorize, type Colorize } from './colorize.js';
import { printGraphNode } from './print.js';
import type { UnresolvedRule } from './type-guards.js';
import type { Pointers } from './types-pointers.js';

export class GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;

  constructor(stackId: number, pathId: number, stepId: number) {
    this.stackId = stackId;
    this.pathId = pathId;
    this.stepId = stepId;
  }
}

export class GraphNode {
  rule: UnresolvedRule;
  next: GraphNode | undefined;
  meta: GraphNodeMeta;
  private _id: string | undefined = undefined;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
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

  print(colorize: Colorize = defaultColorize, pointers?: Pointers, showPosition = false): string {
    return printGraphNode(this, colorize, pointers, showPosition);
  }

  toString(): string {
    return this.print(defaultColorize, undefined, false);
  }
}
