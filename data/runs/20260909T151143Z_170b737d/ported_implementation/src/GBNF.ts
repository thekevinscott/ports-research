import { Graph } from "./grammar_graph/graph.ts";
import { ParseState } from "./grammar_graph/parse_state.ts";
import { build_rule_stack } from "./grammar_parser/build_rule_stack.ts";
import { GrammarParseError, RulesBuilder } from "./rules_builder/index.ts";

export const GBNF = (grammar: string, initial_string: string = ""): ParseState => {
  if (typeof grammar !== "string") {
    throw new Error("grammar must be a string");
  }

  if (typeof initial_string !== "string") {
    throw new Error("input must be a string");
  }

  const rules_builder = new RulesBuilder(grammar);
  const { rules, symbol_ids } = rules_builder;
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, "No rules were found");
  }
  // Matches the reference: looking up a missing symbol raises rather than
  // returning null, so a grammar without a `root` rule surfaces as a KeyError.
  const root_id: number = symbol_ids.getItem("root");

  const stacked_rules = rules.map((rule) => build_rule_stack(rule));
  const graph = new Graph(grammar, stacked_rules, root_id);
  return new ParseState(graph, graph.add(initial_string));
};
