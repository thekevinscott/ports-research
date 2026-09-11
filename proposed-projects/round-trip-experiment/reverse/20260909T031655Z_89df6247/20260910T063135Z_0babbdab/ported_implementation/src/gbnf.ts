import { Graph, type StackedRules } from './grammarGraph/graph.js';
import { ParseState } from './grammarGraph/parseState.js';
import { buildRuleStack } from './grammarParser/buildRuleStack.js';
import { RulesBuilder } from './rulesBuilder/rulesBuilder.js';
import { GrammarParseError } from './utils/errors/grammarParseError.js';

export const GBNF = (input: string, initialString = ''): ParseState => {
  const grammar = typeof input === 'string' ? input : String(input);
  const builder = new RulesBuilder(grammar);
  const { rules, symbolIds } = builder;
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  if (!symbolIds.has('root')) {
    throw new GrammarParseError(
      grammar,
      0,
      'Grammar does not contain a root symbol. Available symbols are: ' +
        `${symbolIds.keys()}`
    );
  }
  const rootId = symbolIds.get('root');

  const stackedRules: StackedRules = rules.map((rule) =>
    rule !== null ? buildRuleStack(rule) : null
  );
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};

export default GBNF;
