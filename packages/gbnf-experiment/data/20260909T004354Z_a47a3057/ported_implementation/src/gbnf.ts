import { Graph } from './grammar-graph/graph.js';
import { ParseState } from './grammar-graph/parse-state.js';
import { buildRuleStack } from './grammar-parser/build-rule-stack.js';
import { RulesBuilder } from './rules-builder/rules-builder.js';
import { GrammarParseError } from './utils/errors/index.js';

export const GBNF = (grammar: string, initialString = ''): ParseState => {
  if (typeof grammar !== 'string') {
    throw new Error('grammar must be a string');
  }

  if (typeof initialString !== 'string') {
    throw new Error('input must be a string');
  }

  const rulesBuilder = new RulesBuilder(grammar);
  const { rules, symbolIds } = rulesBuilder;
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  const rootId = symbolIds.get('root');
  if (rootId === undefined) {
    throw new GrammarParseError(
      grammar,
      0,
      "Grammar does not contain a 'root' symbol",
    );
  }

  const stackedRules = rules.map((rule) => buildRuleStack(rule));
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};

export default GBNF;
