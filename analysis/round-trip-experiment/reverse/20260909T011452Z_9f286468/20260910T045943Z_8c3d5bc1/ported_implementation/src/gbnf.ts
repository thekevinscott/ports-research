import { Graph } from './grammar-graph/graph';
import { ParseState } from './grammar-graph/parse-state';
import type { UnresolvedRule } from './grammar-graph/type-guards';
import type { ValidInput } from './grammar-graph/types';
import { buildRuleStack } from './grammar-parser/build-rule-stack';
import { RulesBuilder } from './rules-builder/rules-builder';
import { GrammarParseError } from './utils/errors/grammar-parse-error';

export const GBNF = (
  input: unknown,
  initialString: ValidInput = ''
): ParseState => {
  const grammar = typeof input === 'string' ? input : `${input}`;
  const { rules, symbolIds } = new RulesBuilder(grammar);
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  if (!symbolIds.has('root')) {
    const available = JSON.stringify([...symbolIds.keys()]);
    throw new GrammarParseError(
      grammar,
      0,
      `Grammar does not contain a root symbol. Available symbols are: ${available}`
    );
  }
  const rootId = symbolIds.get('root');

  const stackedRules: (UnresolvedRule[][] | undefined)[] = rules.map((rule) =>
    rule !== undefined ? buildRuleStack(rule) : undefined
  );
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};

export default GBNF;
