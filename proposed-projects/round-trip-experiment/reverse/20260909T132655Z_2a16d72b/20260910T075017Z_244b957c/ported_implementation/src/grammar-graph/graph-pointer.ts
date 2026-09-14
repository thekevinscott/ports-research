import { Colorize, colorize as defaultColorize } from './colorize.js';
import { printGraphPointer } from './print.js';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
} from './type-guards.js';
import type { GraphNode } from './graph-node.js';
import type { RuleRef } from './rule-ref.js';
import type { Rule } from './types.js';

export class GraphPointer {
  node: GraphNode;
  parent?: GraphPointer;
  id: string;
  private _valid?: boolean;

  constructor(node: GraphNode, parent?: GraphPointer) {
    if (node === undefined || node === null) {
      throw new Error('Node is undefined');
    }
    this.node = node;
    this.parent = parent;
    this.id = parent ? `${parent.id}-${node.id}` : node.id;
  }

  /**
   * 1. If the current node is an end node, and the pointer has a parent, return the
   *    parent's `fetchNext`; else return nothing.
   * 2. If the current node is a rule ref, yield the referenced nodes, _unless_
   *    resolved is true, in which case it returns next.
   * 3. If the current node is a char or range, we go to the next node. If none
   *    exists, throw an error.
   */
  *resolve(resolved = false): Generator<GraphPointer> {
    if (isGraphPointerRuleRef(this)) {
      if (resolved) {
        if (!this.node.next) {
          throw new Error(`No next node: ${this.node}`);
        }
        yield* new GraphPointer(this.node.next, this.parent).resolve();
      } else {
        for (const node of (this.node.rule as RuleRef).nodes) {
          yield* new GraphPointer(node, this).resolve();
        }
      }
    } else if (isGraphPointerRuleEnd(this)) {
      if (!this.parent) {
        yield this;
      } else {
        yield* this.parent.resolve(true);
      }
    } else if (
      isGraphPointerRuleChar(this) ||
      isGraphPointerRuleCharExclude(this)
    ) {
      yield this;
    } else {
      throw new Error(`Unknown rule: ${this.node.rule}`);
    }
  }

  *fetchNext(): Generator<GraphPointer> {
    // if this pointer is invalid, then we don't return any new pointers
    if (this._valid === false) {
      return;
    }

    // if this pointer is an end node, we return the parent's next node. If no parent
    // exists, we return nothing, since it's the end of the line.
    if (isRuleEnd(this.node.rule)) {
      if (this.parent) {
        yield* this.parent.fetchNext();
      }
    } else {
      if (!this.node.next) {
        throw new Error(`No next node: ${this.node}`);
      }
      yield* new GraphPointer(this.node.next, this.parent).resolve();
    }
  }

  get rule(): Rule | RuleRef {
    return this.node.rule;
  }

  get valid(): boolean | undefined {
    return this._valid;
  }

  set valid(valid: boolean | undefined) {
    this._valid = valid;
  }

  print(colorize: Colorize = defaultColorize): string {
    return printGraphPointer(this, colorize);
  }

  toString(): string {
    return this.print((v) => `${v}`);
  }
}
