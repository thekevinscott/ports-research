import { Graph } from './grammarGraph/graph.js';
import { ParseState } from './grammarGraph/parseState.js';
import type { UnresolvedRule, ValidInput } from './grammarGraph/types.js';
import { buildRuleStack } from './grammarParser/buildRuleStack.js';
import { RulesBuilder } from './rulesBuilder/rulesBuilder.js';
import { GrammarParseError } from './utils/errors/GrammarParseError.js';

export const GBNF = (input: unknown, initialString: ValidInput = ''): ParseState => {
  const grammar = typeof input === 'string' ? input : `${input}`;
  const { rules, symbolIds } = new RulesBuilder(grammar);
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  if (!symbolIds.has('root')) {
    // the symbols are rendered with a space after each comma, as the reference does
    const symbols = [...symbolIds.keys()].map(key => JSON.stringify(key)).join(', ');
    throw new GrammarParseError(
      grammar,
      0,
      `Grammar does not contain a root symbol. Available symbols are: [${symbols}]`,
    );
  }
  const rootId = symbolIds.get('root');

  const stackedRules: (UnresolvedRule[][] | null)[] = rules.map(
    rule => rule !== null ? buildRuleStack(rule) : null,
  );
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};

export default GBNF;
