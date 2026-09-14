import { Graph } from './grammar-graph/graph';
import { ParseState } from './grammar-graph/parse-state';
import type { UnresolvedRule, ValidInput } from './grammar-graph/types';
import { buildRuleStack } from './grammar-parser/build-rule-stack';
import { RulesBuilder } from './rules-builder/rules-builder';
import { GrammarParseError } from './utils/errors/grammar-parse-error';

/**
 * Parse a GBNF grammar and return the resulting `ParseState`.
 *
 * Throws `GrammarParseError` if the grammar is invalid, and `InputParseError`
 * if `initialString` cannot be parsed by the grammar.
 */
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
      `Grammar does not contain a root symbol. Available symbols are: ${JSON.stringify(
        symbolIds.keys()
      )}`
    );
  }
  const rootId = symbolIds.get('root');

  const stackedRules: (UnresolvedRule[][] | undefined)[] = rules.map((rule) =>
    rule ? buildRuleStack(rule) : undefined
  );
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};

export default GBNF;
