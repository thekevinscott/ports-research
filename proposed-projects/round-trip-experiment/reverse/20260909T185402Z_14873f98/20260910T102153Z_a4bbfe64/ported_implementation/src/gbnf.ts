import { Graph } from './grammarGraph/graph';
import { ParseState } from './grammarGraph/parseState';
import type { UnresolvedRule, ValidInput } from './grammarGraph/types';
import { buildRuleStack } from './grammarParser/buildRuleStack';
import { RulesBuilder } from './rulesBuilder';
import { GrammarParseError } from './utils/errors/grammarParseError';

export const GBNF = (input: string, initialString: ValidInput = ''): ParseState => {
  const grammar = typeof input === 'string' ? input : String(input);
  const { rules, symbolIds } = new RulesBuilder(grammar);
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  if (!symbolIds.has('root')) {
    const available = JSON.stringify([...symbolIds.keys()]);
    throw new GrammarParseError(
      grammar,
      0,
      `Grammar does not contain a root symbol. Available symbols are: ${available}`,
    );
  }
  const rootId = symbolIds.get('root');

  const stackedRules: (UnresolvedRule[][] | undefined)[] = rules.map((rule) =>
    rule !== undefined ? buildRuleStack(rule) : undefined,
  );
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};
