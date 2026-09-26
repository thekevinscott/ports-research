import { printGraphPointer } from './print.ts';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
} from './type_guards.ts';

import type {
  PrintOpts,
  ResolvedGraphPointer,
  UnresolvedRule,
} from './grammar_graph_types.ts';
import type { GraphNode } from './graph_node.ts';

export type GraphPointerKey = string;

export class GraphPointer<T extends UnresolvedRule = UnresolvedRule> {
  node: GraphNode<T>;
  parent: GraphPointer | undefined;
  id: string;

  private __valid__: boolean | undefined = undefined;

  constructor(node: GraphNode<T>, parent?: GraphPointer) {
    if (node === undefined || node === null) {
      throw new Error('Node is undefined');
    }
    this.node = node;
    this.parent = parent ?? undefined;
    this.id = parent ? `${parent.id}-${node.id}` : node.id;
  }

  get rule(): T {
    return this.node.rule;
  }

  get valid(): boolean | undefined {
    return this.__valid__;
  }

  set valid(valid: boolean | undefined) {
    this.__valid__ = valid;
  }

  print(opts: PrintOpts): string {
    return printGraphPointer(this as GraphPointer)(opts);
  }

  /**
   * Resolve the graph pointer, yielding pointers that point at a concrete
   * (non reference) rule.
   */
  *resolve(resolved = false): Generator<ResolvedGraphPointer> {
    const pointer = this as GraphPointer;
    if (isGraphPointerRuleRef(pointer)) {
      if (resolved) {
        if (!pointer.node.next) {
          throw new Error(`No next node: ${pointer.node.id}`);
        }
        yield* new GraphPointer(pointer.node.next, pointer.parent).resolve();
      } else {
        for (const node of pointer.rule.nodes) {
          yield* new GraphPointer(node, pointer).resolve();
        }
      }
    } else if (isGraphPointerRuleEnd(pointer)) {
      if (!pointer.parent) {
        yield pointer as ResolvedGraphPointer;
      } else {
        yield* pointer.parent.resolve(true);
      }
    } else if (isGraphPointerRuleChar(pointer) || isGraphPointerRuleCharExclude(pointer)) {
      yield pointer as ResolvedGraphPointer;
    } else {
      throw new Error(`Unknown rule: ${pointer.node.rule}`);
    }
  }

  /**
   * Fetch the next resolved graph pointers.
   */
  *fetchNext(): Generator<ResolvedGraphPointer> {
    // If this pointer is invalid, then we don't return any new pointers
    if (!this.valid) {
      return;
    }

    // If this pointer is an end node, we return the parent's next node.
    // If no parent exists, we return nothing, since it's the end of the line.
    if (isRuleEnd(this.node.rule)) {
      if (this.parent) {
        yield* this.parent.fetchNext();
      }
    } else {
      if (!this.node.next) {
        throw new Error(`No next node: ${this.node.id}`);
      }
      const pointer = new GraphPointer(this.node.next, this.parent);
      yield* pointer.resolve();
    }
  }

  fetch_next(): Generator<ResolvedGraphPointer> {
    return this.fetchNext();
  }
}
