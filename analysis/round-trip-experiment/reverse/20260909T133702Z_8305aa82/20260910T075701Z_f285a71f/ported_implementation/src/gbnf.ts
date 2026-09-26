import { Graph } from './grammar-graph/graph.js';
import { ParseState } from './grammar-graph/parse-state.js';
import type { Rule } from './grammar-graph/type-guards.js';
import type { ValidInput } from './grammar-graph/types.js';
import { buildRuleStack } from './grammar-parser/build-rule-stack.js';
import { RulesBuilder } from './rules-builder/rules-builder.js';
import { GrammarParseError } from './utils/errors/grammar-parse-error.js';

export const GBNF = (
  input: string,
  initialString: ValidInput = '',
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
      `Grammar does not contain a root symbol. Available symbols are: ${JSON.stringify(
        symbolIds.keys(),
      )}`,
    );
  }
  const rootId = symbolIds.get('root');

  const stackedRules: (Rule[][] | null)[] = rules.map((rule) =>
    rule !== null ? buildRuleStack(rule) : null,
  );
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};

export default GBNF;
