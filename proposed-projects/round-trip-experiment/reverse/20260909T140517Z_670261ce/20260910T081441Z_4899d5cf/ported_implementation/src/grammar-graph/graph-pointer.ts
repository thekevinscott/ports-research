import { colorize, type Colorize } from './colorize.js';
import type { GraphNode } from './graph-node.js';
import { printGraphPointer } from './print.js';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
  type UnresolvedRule,
} from './type-guards.js';

/**
 * Resolving a grammar whose repetition can match the empty string (`a ::= "b"?`
 * used as `a*`) never terminates: it keeps nesting pointers forever. Walking the
 * graph iteratively means there is no call stack to run out of, so this is the
 * explicit bound, kept well above any depth a real grammar reaches.
 */
export const MAX_POINTER_DEPTH = 5000;

export class GraphPointer {
  public readonly node: GraphNode;
  public readonly parent: GraphPointer | undefined;
  public readonly id: string;
  public readonly depth: number;
  public readonly print: (opts: { colorize: Colorize }) => string;

  public valid: boolean | undefined = undefined;

  constructor(node: GraphNode, parent?: GraphPointer) {
    if (!node) {
      throw new Error('Node is undefined');
    }
    this.node = node;
    this.parent = parent;
    this.id = parent ? `${parent.id}-${node.id}` : node.id;
    this.depth = parent ? parent.depth + 1 : 0;
    this.print = printGraphPointer(this);
  }

  /**
   * 1. If the current node is an end node, and the pointer has a parent, return the
   *    parent's `fetchNext`; else return nothing.
   * 2. If the current node is a rule ref, yield the referenced nodes, _unless_
   *    resolved is true, in which case it returns next.
   * 3. If the current node is a char or range, we go to the next node. If none
   *    exists, throw an error.
   *
   * Walked with an explicit stack (depth first, same order as recursing) so that a
   * deeply nested grammar cannot overrun the call stack.
   */
  *resolve(resolved = false): IterableIterator<GraphPointer> {
    const stack: [GraphPointer, boolean][] = [[this, resolved]];
    while (stack.length) {
      const [pointer, isResolved] = stack.pop() as [GraphPointer, boolean];
      if (isGraphPointerRuleRef(pointer)) {
        if (isResolved) {
          if (!pointer.node.next) {
            throw new Error(`No next node: ${pointer.node}`);
          }
          stack.push([new GraphPointer(pointer.node.next, pointer.parent), false]);
        } else {
          if (pointer.depth >= MAX_POINTER_DEPTH) {
            throw new RangeError(
              'Maximum grammar depth exceeded; the grammar is most likely infinitely ' +
                'recursive (for instance a rule that can match the empty string used ' +
                'with "*" or "+")'
            );
          }
          const { nodes } = pointer.rule;
          for (let i = nodes.length - 1; i >= 0; i -= 1) {
            stack.push([new GraphPointer(nodes[i], pointer), false]);
          }
        }
      } else if (isGraphPointerRuleEnd(pointer)) {
        if (!pointer.parent) {
          yield pointer;
        } else {
          stack.push([pointer.parent, true]);
        }
      } else if (isGraphPointerRuleChar(pointer) || isGraphPointerRuleCharExclude(pointer)) {
        yield pointer;
      } else {
        throw new Error(`Unknown rule: ${pointer.node.rule}`);
      }
    }
  }

  *fetchNext(): IterableIterator<GraphPointer> {
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
        continue;
      }

      if (!pointer.node.next) {
        throw new Error(`No next node: ${pointer.node}`);
      }
      yield* new GraphPointer(pointer.node.next, pointer.parent).resolve();
      return;
    }
  }

  get rule(): UnresolvedRule {
    return this.node.rule;
  }

  toString(): string {
    return this.print({ colorize });
  }
}
