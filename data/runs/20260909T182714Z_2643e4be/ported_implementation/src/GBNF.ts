import { Graph } from "./grammar-graph/graph.js";
import { ParseState } from "./grammar-graph/parse-state.js";
import { buildRuleStack } from "./grammar-parser/build-rule-stack.js";
import { GrammarParseError, RulesBuilder } from "./rules-builder/index.js";
import { ValueError } from "./utils/errors/python-errors.js";

export const GBNF = (grammar: string, initialString = ""): ParseState => {
  if (typeof grammar !== "string") {
    throw new ValueError("grammar must be a string");
  }

  if (typeof initialString !== "string") {
    throw new ValueError("input must be a string");
  }

  const rulesBuilder = new RulesBuilder(grammar);
  const { rules, symbolIds } = rulesBuilder;
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, "No rules were found");
  }
  // as in the reference implementation, a grammar without a root symbol raises
  // a KeyError from this lookup before the check below can report on it.
  if (symbolIds.get("root") === null) {
    throw new GrammarParseError(
      grammar,
      0,
      "Grammar does not contain a 'root' symbol",
    );
  }
  const rootId: number = symbolIds.get("root");

  const stackedRules = rules.map((rule) => buildRuleStack(rule));
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};
