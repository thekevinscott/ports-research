import { colorize, Colorize } from './colorize.js';
import type { GraphPointer } from './graph-pointer.js';
import { printGraphNode } from './print.js';
import type { Rule } from './type-guards.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  public rule: Rule;
  public meta: GraphNodeMeta;
  public next?: GraphNode;
  private _id?: string;

  constructor(rule: Rule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (meta === undefined || meta === null) {
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

  print({
    pointers,
    showPosition = false,
    colorize: col = colorize,
  }: {
    pointers?: Iterable<GraphPointer>;
    showPosition?: boolean;
    colorize?: Colorize;
  } = {}): string {
    return printGraphNode(this, { pointers, showPosition, colorize: col });
  }

  toString(): string {
    return this.print({
      colorize: (s) => `${s}`,
      showPosition: false,
    });
  }
}
