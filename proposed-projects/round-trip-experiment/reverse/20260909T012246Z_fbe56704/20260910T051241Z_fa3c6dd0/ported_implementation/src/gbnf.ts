import { Graph } from './grammar-graph/graph.ts';
import { ParseState } from './grammar-graph/parse-state.ts';
import type { UnresolvedRule, ValidInput } from './grammar-graph/types.ts';
import { buildRuleStack } from './grammar-parser/build-rule-stack.ts';
import { RulesBuilder } from './rules-builder/rules-builder.ts';
import { GrammarParseError } from './utils/errors/grammar-parse-error.ts';

export const GBNF = (input: string, initialString: ValidInput = ''): ParseState => {
  const grammar = typeof input === 'string' ? input : String(input);
  const { rules, symbolIds } = new RulesBuilder(grammar);
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  if (!symbolIds.has('root')) {
    throw new GrammarParseError(
      grammar,
      0,
      `Grammar does not contain a root symbol. Available symbols are: [${symbolIds
        .keys()
        .map((key) => JSON.stringify(key))
        .join(', ')}]`
    );
  }
  const rootId = symbolIds.get('root');

  // a plain loop, rather than `map`, so that holes left by undefined rules are visited
  const stackedRules: UnresolvedRule[][][] = [];
  for (let ruleId = 0; ruleId < rules.length; ruleId++) {
    stackedRules.push(buildRuleStack(rules[ruleId]));
  }
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};

export default GBNF;
