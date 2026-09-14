/** Port of `gbnf/grammar_graph/graph_pointer.py`. */

import { Colorize, colorize } from './colorize.js';
import { GraphNode } from './graph-node.js';
import { printGraphPointer } from './print.js';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
  isRuleRef,
} from './type-guards.js';
import type { UnresolvedRule } from './types.js';

export class GraphPointer {
  #valid: boolean | undefined = undefined;
  id: string;

  constructor(
    public node: GraphNode,
    public parent?: GraphPointer,
  ) {
    if (node === undefined) {
      throw new Error('Node is undefined');
    }
    this.id = parent !== undefined ? `${parent.id}-${node.id}` : node.id;
  }

  /**
   * 1. If the current node is an end node, and the pointer has a parent, return the
   *    parent's `fetchNext`; else return nothing.
   * 2. If the current node is a rule ref, yield the referenced nodes, _unless_
   *    resolved is true, in which case it returns next.
   * 3. If the current node is a char or range, we go to the next node. If none
   *    exists, throw an error.
   *
   * The walk uses an explicit stack rather than recursion: a pointer's parent chain
   * grows with every repetition of a self-referential rule, so recursing would blow
   * the call stack on long inputs. The stack is LIFO with children pushed in reverse,
   * which reproduces a depth-first, left-to-right yield order.
   */
  *resolve(resolved = false): IterableIterator<GraphPointer> {
    const stack: [GraphPointer, boolean][] = [[this, resolved]];
    while (stack.length) {
      const [pointer, isResolved] = stack.pop() as [GraphPointer, boolean];
      if (isGraphPointerRuleRef(pointer)) {
        if (isResolved) {
          if (pointer.node.next === undefined) {
            throw new Error(`No next node: ${pointer.node}`);
          }
          stack.push([new GraphPointer(pointer.node.next, pointer.parent), false]);
        } else {
          const rule = pointer.node.rule;
          if (!isRuleRef(rule)) {
            throw new Error(`Expected a reference rule: ${rule}`);
          }
          const { nodes } = rule;
          for (let i = nodes.length - 1; i >= 0; i -= 1) {
            stack.push([new GraphPointer(nodes[i], pointer), false]);
          }
        }
      } else if (isGraphPointerRuleEnd(pointer)) {
        if (pointer.parent === undefined) {
          yield pointer;
        } else {
          stack.push([pointer.parent, true]);
        }
      } else if (
        isGraphPointerRuleChar(pointer) ||
        isGraphPointerRuleCharExclude(pointer)
      ) {
        yield pointer;
      } else {
        throw new Error(`Unknown rule: ${pointer.node.rule}`);
      }
    }
  }

  *fetchNext(): IterableIterator<GraphPointer> {
    // Walks up the parent chain iteratively, for the same reason `resolve` does.
    let pointer: GraphPointer | undefined = this;
    while (pointer !== undefined) {
      // if this pointer is invalid, then we don't return any new pointers
      if (pointer.valid === false) {
        return;
      }

      // if this pointer is an end node, we return the parent's next node. If no
      // parent exists, we return nothing, since it's the end of the line.
      if (isRuleEnd(pointer.node.rule)) {
        pointer = pointer.parent;
      } else {
        if (pointer.node.next === undefined) {
          throw new Error(`No next node: ${pointer.node}`);
        }
        yield* new GraphPointer(pointer.node.next, pointer.parent).resolve();
        return;
      }
    }
  }

  get rule(): UnresolvedRule {
    return this.node.rule;
  }

  get valid(): boolean | undefined {
    return this.#valid;
  }

  set valid(valid: boolean) {
    this.#valid = valid;
  }

  print(col: Colorize = colorize): string {
    return printGraphPointer(this, col);
  }

  toString(): string {
    return this.print(colorize);
  }
}
