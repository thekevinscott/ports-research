import { Graph } from './grammar-graph/graph';
import { ParseState } from './grammar-graph/parse-state';
import { buildRuleStack } from './grammar-parser/build-rule-stack';
import { GrammarParseError, RulesBuilder } from './rules-builder';

export const GBNF = (grammar: string, initialString = ''): ParseState => {
  if (typeof grammar !== 'string') {
    throw new Error('grammar must be a string');
  }

  if (typeof initialString !== 'string') {
    throw new Error('input must be a string');
  }

  const { rules, symbolIds } = new RulesBuilder(grammar);
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  const rootId = symbolIds.get('root');
  if (rootId === undefined) {
    throw new GrammarParseError(grammar, 0, "Grammar does not contain a 'root' symbol");
  }

  const stackedRules = rules.map((rule) => buildRuleStack(rule));
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};
