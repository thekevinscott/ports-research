import { Graph, RuleStack } from './grammar-graph/graph.js';
import { ParseState } from './grammar-graph/parse-state.js';
import type { ValidInput } from './grammar-graph/types.js';
import { buildRuleStack } from './grammar-parser/build-rule-stack.js';
import { RulesBuilder } from './rules-builder/rules-builder.js';
import { GrammarParseError } from './utils/errors/grammar-parse-error.js';

export const GBNF = (input: string, initialString: ValidInput = ''): ParseState => {
  const grammar = typeof input === 'string' ? input : String(input);
  const { rules, symbolIds } = new RulesBuilder(grammar);
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  // NOTE: a grammar without a root symbol raises out of `get` ("SymbolIds does
  // not contain key: root") before the nicer "Grammar does not contain a root
  // symbol" error can be raised.
  const rootId = symbolIds.get('root');

  const stackedRules: (RuleStack | undefined)[] = rules.map(rule => (
    rule !== undefined ? buildRuleStack(rule) : undefined
  ));
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};
