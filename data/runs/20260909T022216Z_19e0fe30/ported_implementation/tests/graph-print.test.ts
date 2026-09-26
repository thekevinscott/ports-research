import { describe, expect, it } from 'vitest';

import { Graph } from '../src/grammar-graph/graph.js';
import { buildRuleStack } from '../src/grammar-parser/build-rule-stack.js';
import { RulesBuilder } from '../src/rules-builder/rules-builder.js';

/**
 * `Graph.print` has no coverage in the python suite, and in fact throws there:
 * the reference prints a non-char, non-ref rule as `rule.type`, an attribute
 * its `Rule` classes never define, so any graph containing a `RuleEnd` node --
 * every graph -- raises `AttributeError`. Rules carry a `type` in this port, so
 * printing works; these cases pin the output down.
 */
const buildGraph = (grammar: string): Graph => {
  const rulesBuilder = new RulesBuilder(grammar);
  return new Graph(
    grammar,
    rulesBuilder.rules.map(buildRuleStack),
    rulesBuilder.symbolIds.get('root')!,
  );
};

describe('Graph.print', () => {
  it('prints a single-path grammar', () => {
    expect(buildGraph('root ::= "fo"').print()).toBe(
      ['{0,0,0}[f]-> {0,0,1}[o]-> {0,0,2}end'].join('\n'),
    );
  });

  it('prints alternates, references and ranges', () => {
    expect(buildGraph('root ::= "fo" | [a-z]?').print()).toBe(
      [
        '{0,0,0}[f]-> {0,0,1}[o]-> {0,0,2}end',
        '{0,1,0}Ref(1)-> {0,1,1}end',
        '{1,0,0}[az]-> {1,0,1}end',
        '{1,1,0}end',
      ].join('\n'),
    );
  });

  it('colorizes when asked to', () => {
    const printed = buildGraph('root ::= "f"').print(undefined, true);
    expect(printed).toContain('\x1b[');
    expect(printed.replace(/\x1b\[\d+m/g, '')).toBe('{0,0,0}[f]-> {0,0,1}end');
  });
});
