import { Graph } from './grammar-graph/graph';
import { ParseState } from './grammar-graph/parse-state';
import type { Rule } from './grammar-graph/type-guards';
import type { ValidInput } from './grammar-graph/types';
import { buildRuleStack } from './grammar-parser/build-rule-stack';
import { RulesBuilder } from './rules-builder/rules-builder';
import { GrammarParseError } from './utils/errors/grammar-parse-error';

export const GBNF = (input: string, initialString: ValidInput = ''): ParseState => {
  const grammar = typeof input === 'string' ? input : String(input);
  const rulesBuilder = new RulesBuilder(grammar);
  const { rules, symbolIds } = rulesBuilder;
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  if (!symbolIds.has('root')) {
    throw new GrammarParseError(
      grammar,
      0,
      'Grammar does not contain a root symbol. Available symbols are: ' +
        `${JSON.stringify([...symbolIds.keys()])}`,
    );
  }
  const rootId = symbolIds.get('root');

  const stackedRules: Rule[][][] = rules
    .filter((rule): rule is NonNullable<typeof rule> => rule !== null)
    .map(rule => buildRuleStack(rule));
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};
