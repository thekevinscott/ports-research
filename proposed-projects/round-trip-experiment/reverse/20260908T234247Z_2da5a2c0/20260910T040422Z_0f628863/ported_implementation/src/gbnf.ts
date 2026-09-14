import { Graph } from './grammar-graph/graph.ts';
import { ParseState } from './grammar-graph/parse-state.ts';
import type { UnresolvedRule, ValidInput } from './grammar-graph/types.ts';
import { buildRuleStack } from './grammar-parser/build-rule-stack.ts';
import { RulesBuilder } from './rules-builder/rules-builder.ts';
import { GrammarParseError } from './utils/errors/grammar-parse-error.ts';

export const GBNF = (
  input: string | { toString(): string },
  initialString: ValidInput = ''
): ParseState => {
  const grammar = typeof input === 'string' ? input : String(input);
  const { rules, symbolIds } = new RulesBuilder(grammar);
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  if (!symbolIds.has('root')) {
    throw new GrammarParseError(
      grammar,
      0,
      `Grammar does not contain a root symbol. Available symbols are: ${JSON.stringify([...symbolIds.keys()])}`
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
