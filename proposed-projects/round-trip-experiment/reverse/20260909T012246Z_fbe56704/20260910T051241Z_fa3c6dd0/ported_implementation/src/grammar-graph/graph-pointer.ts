import { colorize as defaultColorize } from './colorize.ts';
import type { Colorize } from './colorize.ts';
import type { GraphNode } from './graph-node.ts';
import { printGraphPointer } from './print.ts';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
  isRuleRef,
} from './type-guards.ts';
import type { UnresolvedRule } from './types.ts';

export type GraphPointerKey = string;

export class GraphPointer {
  node: GraphNode;
  parent: GraphPointer | undefined;
  id: GraphPointerKey;
  private _valid: boolean | undefined;

  constructor(node: GraphNode, parent?: GraphPointer) {
    if (!node) {
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
          throw new Error(`No next node: ${this.node.print()}`);
        }
        yield* new GraphPointer(this.node.next, this.parent).resolve();
      } else {
        const rule = this.node.rule;
        if (!isRuleRef(rule)) {
          throw new Error('Expected a rule ref');
        }
        for (const node of rule.nodes) {
          yield* new GraphPointer(node, this).resolve();
        }
      }
    } else if (isGraphPointerRuleEnd(this)) {
      if (!this.parent) {
        yield this;
      } else {
        yield* this.parent.resolve(true);
      }
    } else if (isGraphPointerRuleChar(this) || isGraphPointerRuleCharExclude(this)) {
      yield this;
    } else {
      throw new Error(`Unknown rule: ${JSON.stringify(this.node.rule)}`);
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
        throw new Error(`No next node: ${this.node.print()}`);
      }
      const pointer = new GraphPointer(this.node.next, this.parent);
      yield* pointer.resolve();
    }
  }

  get rule(): UnresolvedRule {
    return this.node.rule;
  }

  get valid(): boolean | undefined {
    return this._valid;
  }

  set valid(valid: boolean) {
    this._valid = valid;
  }

  print(colorize: Colorize = defaultColorize): string {
    return printGraphPointer(this, colorize);
  }
}
