import { Graph } from './grammar-graph/graph.js';
import { ParseState } from './grammar-graph/parse-state.js';
import type { UnresolvedRule } from './grammar-graph/types.js';
import { buildRuleStack } from './grammar-parser/build-rule-stack.js';
import { RulesBuilder } from './rules-builder/rules-builder.js';
import { GrammarParseError } from './utils/errors/grammar-parse-error.js';

/** Parse a GBNF grammar and return the `ParseState` it starts in. */
export const GBNF = (input: string, initialString = ''): ParseState => {
  const grammar = typeof input === 'string' ? input : String(input);
  const { rules, symbolIds } = new RulesBuilder(grammar);
  if (rules.length === 0) {
    throw new GrammarParseError(grammar, 0, 'No rules were found');
  }
  // `SymbolIds.get` throws a `GBNFError` for an unknown key, so a grammar without a
  // root symbol surfaces as that error before the check below can fire — the reference
  // implementation behaves the same way.
  const rootId: number | undefined = symbolIds.get('root');
  if (rootId === undefined) {
    throw new GrammarParseError(
      grammar,
      0,
      `Grammar does not contain a root symbol. Available symbols are: ${[
        ...symbolIds.keys(),
      ]}`,
    );
  }

  // `rules` may be sparse while sub-rules are generated; holes are carried through,
  // exactly as `Array.prototype.map` does.
  const stackedRules: UnresolvedRule[][][] = rules.map((rule) =>
    rule === undefined ? (undefined as unknown as UnresolvedRule[][]) : buildRuleStack(rule),
  );
  const graph = new Graph(grammar, stackedRules, rootId);
  return new ParseState(graph, graph.add(initialString));
};

export default GBNF;
