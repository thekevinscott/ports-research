import type { GraphNode } from './graph-node.js';
import { printGraphPointer } from './print.js';
import { isRuleChar, isRuleCharExclude, isRuleEnd, isRuleRef } from './type-guards.js';
import type { PrintOpts, ResolvedGraphPointer, UnresolvedRule } from './types.js';

export type GraphPointerKey = string;

export class GraphPointer<T extends UnresolvedRule = UnresolvedRule> {
  node: GraphNode<T>;
  parent?: GraphPointer;
  id: GraphPointerKey;
  #valid?: boolean;

  constructor(node: GraphNode<T>, parent?: GraphPointer) {
    if (!node) {
      throw new Error('Node is undefined');
    }
    this.node = node;
    this.parent = parent;
    this.id = parent ? `${parent.id}-${node.id}` : node.id;
  }

  get rule(): T {
    return this.node.rule;
  }

  get valid(): boolean | undefined {
    return this.#valid;
  }

  set valid(valid: boolean | undefined) {
    this.#valid = valid;
  }

  print(opts: PrintOpts): string {
    return printGraphPointer(this)(opts);
  }

  /**
   * Resolve this pointer into pointers that sit on concrete (non-reference) rules.
   *
   * @param resolved whether the pointer has already been resolved
   */
  *resolve(resolved = false): Generator<ResolvedGraphPointer> {
    const rule = this.rule;
    if (isRuleRef(rule)) {
      if (resolved) {
        if (!this.node.next) {
          throw new Error(`No next node: ${JSON.stringify(this.node.meta)}`);
        }
        yield* new GraphPointer(this.node.next, this.parent).resolve();
      } else {
        for (const node of rule.nodes) {
          yield* new GraphPointer(node, this).resolve();
        }
      }
    } else if (isRuleEnd(rule)) {
      if (!this.parent) {
        yield this as unknown as ResolvedGraphPointer;
      } else {
        yield* this.parent.resolve(true);
      }
    } else if (isRuleChar(rule) || isRuleCharExclude(rule)) {
      yield this as unknown as ResolvedGraphPointer;
    } else {
      throw new Error(`Unknown rule: ${JSON.stringify(rule)}`);
    }
  }

  /**
   * Fetch the pointers that follow this one, if this pointer is still valid.
   */
  *fetchNext(): Generator<GraphPointer> {
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
        throw new Error(`No next node: ${JSON.stringify(this.node.meta)}`);
      }
      yield* new GraphPointer(this.node.next, this.parent).resolve();
    }
  }
}
