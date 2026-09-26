import { colorize } from './colorize';
import type { Colorize } from './colorize';
import type { GraphPointer } from './graphPointer';
import { printGraphNode } from './print';
import type { UnresolvedRule } from './types';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  public rule: UnresolvedRule;
  public meta: GraphNodeMeta;
  public next?: GraphNode;
  private _id?: string;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (meta === undefined) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  get id(): string {
    if (this._id === undefined) {
      const { stackId, pathId, stepId } = this.meta;
      this._id = `${stackId},${pathId},${stepId}`;
    }
    return this._id;
  }

  print(
    colorizeFn: Colorize = colorize,
    pointers?: Iterable<GraphPointer>,
    showPosition = false,
  ): string {
    return printGraphNode(this, colorizeFn, pointers, showPosition);
  }
}
