import { Colorize, colorize as defaultColorize } from './colorize.js';
import type { GraphNode } from './graph-node.js';
import { printGraphPointer } from './print.js';
import type { RuleRef } from './rule-ref.js';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
} from './type-guards.js';
import type { UnresolvedRule } from './types.js';

// How much deeper than its starting point a single `resolve` walk may descend.
// Descending means stepping into a rule reference without consuming any input,
// which a well-formed grammar can only do as many times as it has nested rules.
// A grammar that can match the empty string inside a repetition — `("a"*)+`, say
// — descends forever instead; this bound is how we fail fast on those grammars
// rather than exhausting the stack.
export const MAX_RESOLVE_DEPTH_GROWTH = 1000;

export const MAX_RESOLVE_DEPTH_ERROR_MESSAGE = [
  'Maximum rule depth exceeded; the grammar can descend into a rule',
  'without consuming input, e.g. a repetition of an optional rule',
].join(' ');

export class GraphPointer {
  node: GraphNode;
  parent: GraphPointer | undefined;
  id: string;
  depth: number;
  #valid: boolean | undefined;

  constructor(node: GraphNode, parent?: GraphPointer) {
    if (!node) {
      throw new Error('Node is undefined');
    }
    this.node = node;
    this.parent = parent;
    this.id = parent ? `${parent.id}-${node.id}` : node.id;
    this.depth = parent ? parent.depth + 1 : 0;
  }

  /**
   * 1. If the current node is an end node, and the pointer has a parent, return the parent's `fetchNext`; else return nothing.
   * 2. If the current node is a rule ref, yield the referenced nodes, _unless_ resolved is true, in which case it returns next.
   * 3. If the current node is a char or range, we go to the next node. If none exists, throw an error.
   *
   * Walked with an explicit stack rather than recursively: the parent chain
   * grows with the depth of the parse, which is unbounded.
   */
  *resolve(resolved = false): Generator<GraphPointer> {
    // LIFO, so pushing the referenced nodes in reverse keeps the depth-first
    // order the recursive form yields in.
    const maxDepth = this.depth + MAX_RESOLVE_DEPTH_GROWTH;
    const stack: [GraphPointer, boolean][] = [[this, resolved]];
    while (stack.length) {
      const [pointer, isResolved] = stack.pop() as [GraphPointer, boolean];
      if (pointer.depth > maxDepth) {
        // a RangeError, as an exhausted stack would be
        throw new RangeError(MAX_RESOLVE_DEPTH_ERROR_MESSAGE);
      }
      if (isGraphPointerRuleRef(pointer)) {
        if (isResolved) {
          if (!pointer.node.next) {
            throw new Error(`No next node: ${pointer.node}`);
          }
          stack.push([new GraphPointer(pointer.node.next, pointer.parent), false]);
        } else {
          const { nodes } = pointer.node.rule as RuleRef;
          for (let i = nodes.length - 1; i >= 0; i--) {
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

  *fetchNext(): Generator<GraphPointer> {
    let pointer: GraphPointer | undefined = this;
    while (pointer !== undefined) {
      // if this pointer is invalid, then we don't return any new pointers
      if (pointer.valid === false) {
        return;
      }

      // if this pointer is an end node, we return the parent's next node. If no parent exists,
      // we return nothing, since it's the end of the line.
      if (isRuleEnd(pointer.node.rule)) {
        pointer = pointer.parent;
      } else {
        if (!pointer.node.next) {
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

  set valid(valid: boolean | undefined) {
    this.#valid = valid;
  }

  print(colorize: Colorize = defaultColorize): string {
    return printGraphPointer(this, colorize);
  }

  toString(): string {
    return this.print();
  }
}
