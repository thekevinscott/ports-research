import type { GraphNode } from './graph_node.ts';
import { RuleType } from './rule_type.ts';

/**
 * A reference to another rule in the graph. Rule refs are resolved while
 * walking the graph and are never exposed to the end user.
 */
export class RuleRef {
  readonly type = RuleType.REF;
  value: number;

  private __nodes__: Set<GraphNode> | undefined = undefined;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this.__nodes__ === undefined) {
      throw new Error('Nodes are not set');
    }
    return this.__nodes__;
  }

  set nodes(nodes: Set<GraphNode>) {
    this.__nodes__ = nodes;
  }

  equals(other: unknown): boolean {
    return other instanceof RuleRef && this.value === other.value;
  }
}
