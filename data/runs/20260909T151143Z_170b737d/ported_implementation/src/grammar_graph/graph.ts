import { InputParseError } from "../utils/errors/index.ts";
import { is_point_in_range } from "../utils/is_point_in_range.ts";
import { colorize } from "./colorize.ts";
import { get_input_as_code_points } from "./get_input_as_code_points.ts";
import { get_serialized_rule_key } from "./get_serialized_rule_key.ts";
import type {
  ResolvedGraphPointer,
  UnresolvedRule,
  ValidInput,
} from "./grammar_graph_types.ts";
import { GraphNode } from "./graph_node.ts";
import { GraphPointer } from "./graph_pointer.ts";
import { Pointers } from "./pointers.ts";
import type { RuleRef } from "./rule_ref.ts";
import {
  is_range,
  is_rule_char,
  is_rule_char_exclude,
  is_rule_end,
  is_rule_ref,
} from "./type_guards.ts";

export type RootNode = Map<number, GraphNode>;

export class Graph {
  __roots__: Map<number, RootNode>;
  grammar: string;
  __rootNode__: RootNode | null;
  previous_code_points: number[];

  constructor(grammar: string, stacked_rules: UnresolvedRule[][][], root_id: number) {
    this.__roots__ = new Map();
    this.grammar = grammar;
    this.previous_code_points = [];
    const rule_refs: RuleRef[] = [];
    const unique_rules = new Map<string, UnresolvedRule>();

    for (let stack_id = 0; stack_id < stacked_rules.length; stack_id++) {
      const stack = stacked_rules[stack_id];
      const nodes: RootNode = new Map();
      for (let path_id = 0; path_id < stack.length; path_id++) {
        const path = stack[path_id];
        let node: GraphNode | null = null;
        for (let step_id = path.length - 1; step_id >= 0; step_id--) {
          const next_node: GraphNode | null = node;
          const rule = stack[path_id][step_id];
          unique_rules.set(get_serialized_rule_key(rule), rule);
          if (is_rule_ref(rule)) {
            rule_refs.push(rule);
          }
          // rules coming in may be identical but have different references.
          // here, we ensure we always use the same reference for an identical rule.
          // this makes future comparisons easier.
          const unique_rule = unique_rules.get(get_serialized_rule_key(rule));
          if (unique_rule === undefined) {
            throw new Error("Could not get unique rule");
          }
          node = new GraphNode(
            unique_rule,
            {
              stackId: stack_id,
              pathId: path_id,
              stepId: step_id,
            },
            next_node,
          );
        }

        if (node === null) {
          throw new Error("Could not get node");
        }
        nodes.set(path_id, node);
      }
      this.__roots__.set(stack_id, nodes);
    }

    const root_node = this.__roots__.get(root_id);
    if (root_node === undefined) {
      throw new Error(`Root node not found for value: ${root_id}`);
    }
    this.__rootNode__ = root_node;

    for (const rule_ref of rule_refs) {
      const referenced_nodes = new Set<GraphNode>();
      for (const node of this.__get_root_node__(rule_ref.value).values()) {
        referenced_nodes.add(node);
      }
      rule_ref.nodes = referenced_nodes;
    }
  }

  __get_root_node__(value: number): RootNode {
    const root_node = this.__roots__.get(value);
    if (root_node === undefined) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return root_node;
  }

  __get_initial_pointers__(): Pointers {
    const pointers = new Pointers();

    const root_node = this.__rootNode__;
    if (root_node === null) {
      throw new Error("Root node is not defined");
    }

    for (const [node, parent] of this.__fetch_nodes_for_root_node__(root_node)) {
      const pointer = new GraphPointer(node, parent);
      for (const resolvedPointer of this.__resolve_pointer__(pointer)) {
        pointers.add(resolvedPointer);
      }
    }
    return pointers;
  }

  __set_valid__(pointers: GraphPointer[], valid: boolean): void {
    for (const pointer of pointers) {
      pointer.valid = valid;
    }
  }

  __parse__(current_pointers: Pointers, code_point: number): Pointers {
    for (const [rule, graph_pointers] of this.__iterate_over_pointers__(current_pointers)) {
      if (is_rule_char(rule)) {
        let valid = false;
        for (const possible_code_point of rule.value) {
          if (valid === true) {
            // already matched
          } else if (is_range(possible_code_point)) {
            if (is_point_in_range(code_point, possible_code_point)) {
              valid = true;
            }
          } else if (code_point === possible_code_point) {
            valid = true;
          }
        }
        this.__set_valid__(graph_pointers, valid);
      } else if (is_rule_char_exclude(rule)) {
        let valid = true;
        for (const possible_code_point of rule.value) {
          if (valid === false) {
            // already excluded
          } else if (is_range(possible_code_point)) {
            if (is_point_in_range(code_point, possible_code_point)) {
              valid = false;
            }
          } else {
            if (code_point === possible_code_point) {
              valid = false;
            }
          }
        }
        this.__set_valid__(graph_pointers, valid);
      } else if (!is_rule_end(rule)) {
        throw new Error(`Unsupported rule: ${rule}`);
      }
    }

    // a pointer's id is the sum of its node's id and its parent's id chain.
    // if two pointers share the same id, it means they point to the same node and have identical parent chains.
    // for the purposes of walking the graph, we only need to keep one of them.
    const next_pointers = new Pointers();
    for (const current_pointer of current_pointers) {
      for (const unresolved_next_pointer of current_pointer.fetch_next()) {
        for (const resolved_next_pointer of this.__resolve_pointer__(unresolved_next_pointer)) {
          next_pointers.add(resolved_next_pointer);
        }
      }
    }
    return next_pointers;
  }

  *__resolve_pointer__(unresolved_pointer: GraphPointer): Generator<ResolvedGraphPointer> {
    for (const resolved_pointer of unresolved_pointer.resolve()) {
      if (is_rule_ref(resolved_pointer.node.rule)) {
        throw new Error("Encountered a reference rule when building pointers to the graph");
      }
      if (is_rule_end(resolved_pointer.node.rule) && resolved_pointer.parent !== null) {
        throw new Error(
          "Encountered an ending rule with a parent when building pointers to the graph",
        );
      }
      yield resolved_pointer as ResolvedGraphPointer;
    }
  }

  add(src: ValidInput, pointers: Pointers | null = null): Pointers {
    if (typeof src !== "string") {
      throw new Error("src must be a string in graph.add");
    }
    // The reference uses `pointers or self.__get_initial_pointers__()`, so an
    // empty `Pointers` also falls back to the initial pointers.
    let current: Pointers =
      pointers !== null && pointers !== undefined && pointers.length > 0
        ? pointers
        : this.__get_initial_pointers__();

    const code_points = get_input_as_code_points(src);
    for (const code_point of code_points) {
      if (!Number.isInteger(code_point)) {
        throw new Error("code_point must be an integer!");
      }
    }

    for (let code_point_pos = 0; code_point_pos < code_points.length; code_point_pos++) {
      const code_point = code_points[code_point_pos];
      current = this.__parse__(current, code_point);
      if (current.length === 0) {
        throw new InputParseError(code_points, code_point_pos, this.previous_code_points);
      }
    }
    this.previous_code_points.push(...code_points);
    return current;
  }

  // generator that yields either the node, or if a reference rule, the referenced node
  // we need these function, as distinct from leveraging the logic in GraphPointer,
  // because that needs a rule ref with already defined nodes; this function is used to _set_ those nodes
  *__fetch_nodes_for_root_node__(
    root_nodes: RootNode,
    parent: GraphPointer | null = null,
  ): Generator<[GraphNode, GraphPointer | null]> {
    for (const node of root_nodes.values()) {
      if (is_rule_ref(node.rule)) {
        yield* this.__fetch_nodes_for_root_node__(
          this.__get_root_node__(node.rule.value),
          new GraphPointer(node, parent),
        );
      } else {
        yield [node, parent];
      }
    }
  }

  print(pointers: Pointers | null = null, colors: boolean = false): string {
    const nodes: GraphNode[][] = [...this.__roots__.values()].map((root_node) => [
      ...root_node.values(),
    ]);
    const resolved_pointers = pointers ?? new Pointers();
    const graph_view: string[] = [];
    for (const root_node of nodes) {
      for (const node of root_node) {
        graph_view.push(
          node.print({
            pointers: resolved_pointers,
            show_position: true,
            colorize: colors ? colorize : (s) => String(s),
          }),
        );
      }
    }

    return graph_view.join("\n");
  }

  *__iterate_over_pointers__(
    pointers: Iterable<GraphPointer>,
  ): Generator<[UnresolvedRule, GraphPointer[]]> {
    // Keyed by rule identity: the reference's `Rule.__hash__` is `id(self)`, so
    // equal-but-distinct rule objects are distinct keys.
    const seen_rules = new Map<UnresolvedRule, GraphPointer[]>();
    for (const pointer of pointers) {
      const rule = pointer.rule;
      if (is_rule_ref(rule)) {
        throw new Error("Encountered a reference rule in the graph");
      }

      let seen_rule = seen_rules.get(rule);
      if (seen_rule === undefined) {
        seen_rule = [pointer];
        seen_rules.set(rule, seen_rule);
      }
      seen_rule.push(pointer);
    }

    yield* seen_rules.entries();
  }
}
