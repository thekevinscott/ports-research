import type { PrintOpts, UnresolvedRule } from "./grammar_graph_types.ts";
import type { GraphNode } from "./graph_node.ts";
import { print_graph_pointer } from "./print.ts";
import {
  is_graph_pointer_rule_char,
  is_graph_pointer_rule_char_exclude,
  is_graph_pointer_rule_end,
  is_graph_pointer_rule_ref,
  is_rule_end,
} from "./type_guards.ts";

export type GraphPointerKey = string;

export class GraphPointer<T extends UnresolvedRule = UnresolvedRule> {
  node: GraphNode<T>;
  parent: GraphPointer | null;
  id: string;
  private __valid__: boolean | null = null;

  constructor(node: GraphNode<T>, parent: GraphPointer | null = null) {
    if (node === null || node === undefined) {
      throw new Error("Node is undefined");
    }
    this.node = node;
    this.parent = parent;
    this.id = parent ? `${parent.id}-${node.id}` : node.id;
  }

  get rule(): T {
    return this.node.rule;
  }

  get valid(): boolean | null {
    return this.__valid__;
  }

  set valid(valid: boolean | null) {
    this.__valid__ = valid;
  }

  print(opts: PrintOpts): string {
    return print_graph_pointer(this as GraphPointer)(opts);
  }

  /**
   * Resolve the graph pointer.
   *
   * @param resolved Whether the pointer has already been resolved.
   * @yields the resolved graph pointers.
   */
  *resolve(resolved: boolean = false): Generator<GraphPointer> {
    const self = this as GraphPointer;
    if (is_graph_pointer_rule_ref(self)) {
      if (resolved) {
        if (!this.node.next) {
          throw new Error(`No next node: ${this.node}`);
        }
        yield* new GraphPointer(this.node.next, this.parent).resolve();
      } else {
        for (const node of self.rule.nodes) {
          yield* new GraphPointer(node, self).resolve();
        }
      }
    } else if (is_graph_pointer_rule_end(self)) {
      if (!this.parent) {
        yield self;
      } else {
        yield* this.parent.resolve(true);
      }
    } else if (is_graph_pointer_rule_char(self) || is_graph_pointer_rule_char_exclude(self)) {
      yield self;
    } else {
      throw new Error(`Unknown rule: ${this.node.rule}`);
    }
  }

  /**
   * Fetch the next resolved graph pointers.
   */
  *fetch_next(): Generator<GraphPointer> {
    // If this pointer is invalid, then we don't return any new pointers
    if (!this.valid) {
      return;
    }

    // If this pointer is an end node, we return the parent's next node.
    // If no parent exists, we return nothing, since it's the end of the line.
    if (is_rule_end(this.node.rule)) {
      if (this.parent) {
        yield* this.parent.fetch_next();
      }
    } else {
      if (!this.node.next) {
        throw new Error(`No next node: ${this.node}`);
      }
      const pointer = new GraphPointer(this.node.next, this.parent);
      yield* pointer.resolve();
    }
  }

  toString(): string {
    return `<GraphPointer ${this.id} ${this.node}>`;
  }
}
