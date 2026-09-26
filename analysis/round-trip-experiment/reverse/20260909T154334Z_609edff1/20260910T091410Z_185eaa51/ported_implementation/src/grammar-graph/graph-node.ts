import { printGraphNode, PrintOpts } from './print';
import type { Rule } from './type-guards';

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
  rule: Rule;
  meta: GraphNodeMeta;
  next?: GraphNode;
  private cachedId?: string;

  constructor(rule: Rule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (meta === undefined) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  get id(): string {
    if (!this.cachedId) {
      this.cachedId = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.cachedId;
  }

  print(opts: PrintOpts = {}): string {
    return printGraphNode(this, opts);
  }

  toString(): string {
    return this.print({ showPosition: false, colorize: string => `${string}` });
  }
}
