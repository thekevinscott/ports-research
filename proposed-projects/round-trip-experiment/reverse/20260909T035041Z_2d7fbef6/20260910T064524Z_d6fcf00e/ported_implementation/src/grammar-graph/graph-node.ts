import { GBNFError } from '../utils/errors/gbnf-error.js';
import { colorize as defaultColorize, Colorize } from './colorize.js';
import type { GenericSet } from './generic-set.js';
import type { GraphPointer } from './graph-pointer.js';
import { printGraphNode } from './print.js';
import type { UnresolvedRule } from './types.js';

export class GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;

  constructor(stackId: number, pathId: number, stepId: number) {
    this.stackId = stackId;
    this.pathId = pathId;
    this.stepId = stepId;
  }

  toString(): string {
    return `{stackId: ${this.stackId}, pathId: ${this.pathId}, stepId: ${this.stepId}}`;
  }
}

export class GraphNode {
  rule: UnresolvedRule;
  meta: GraphNodeMeta;
  next: GraphNode | undefined;
  private _id: string | undefined = undefined;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (!meta) {
      throw new GBNFError('Meta is undefined');
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

  print(
    colorize: Colorize = defaultColorize,
    pointers?: GenericSet<GraphPointer, string>,
    showPosition = false,
  ): string {
    return printGraphNode(this, colorize, pointers, showPosition);
  }

  toString(): string {
    return this.print(defaultColorize, undefined, false);
  }
}
