import { Graph } from './grammar_graph/graph.ts';
import { ParseState } from './grammar_graph/parse_state.ts';
import { buildRuleStack } from './grammar_parser/build_rule_stack.ts';
import { GrammarParseError, RulesBuilder } from './rules_builder/index.ts';

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
  if (symbolIds.get('root') === undefined) {
    throw new GrammarParseError(grammar, 0, "Grammar does not contain a 'root' symbol");
  }
  const rootId: number = symbolIds.get('root') as number;

  const stackedRules = rules.map((rule) => buildRuleStack(rule));
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};

export default GBNF;
