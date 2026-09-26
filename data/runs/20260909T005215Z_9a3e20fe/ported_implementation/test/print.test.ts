import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { Color } from '../src/grammarGraph/colorize.ts';
import { RuleChar, RuleEnd } from '../src/grammarGraph/grammarGraphTypes.ts';
import type { PrintOpts, UnresolvedRule } from '../src/grammarGraph/grammarGraphTypes.ts';
import { GraphNode } from '../src/grammarGraph/graphNode.ts';
import { GraphPointer } from '../src/grammarGraph/graphPointer.ts';
import { printGraphNode, printGraphPointer } from '../src/grammarGraph/print.ts';
import { RuleRef } from '../src/grammarGraph/ruleRef.ts';

const COLORS: Record<string, string> = {
  '\x1b[34m': 'BLUE',
  '\x1b[36m': 'CYAN',
  '\x1b[32m': 'GREEN',
  '\x1b[31m': 'RED',
  '\x1b[90m': 'GRAY',
  '\x1b[33m': 'YELLOW',
};

const mockColorize = (text: string | number, color: string): string => {
  if (!(color in COLORS)) {
    throw new Error(`Invalid color: ${color}`);
  }
  return `[${COLORS[color]}]:${text}`;
};

/** A stand-in for GraphNode that lets a test pick the node's rendered id. */
const createMockNode = (
  id: string,
  rule: UnresolvedRule,
  next: GraphNode | null = null,
): GraphNode => ({ id, rule, next, print: (opts: PrintOpts) => `Node(${id})` }) as GraphNode;

describe('print', () => {
  describe('printGraphPointer', () => {
    it('prints graph pointer details correctly', () => {
      const parent = new GraphPointer(
        new GraphNode(new RuleEnd(), { stackId: 1, pathId: 1, stepId: 1 }),
      );
      const pointer = new GraphPointer(
        new GraphNode(new RuleRef(100), { stackId: 2, pathId: 2, stepId: 2 }),
        parent,
      );
      const result = printGraphPointer(pointer)({
        colorize: mockColorize,
        showPosition: false,
      });
      assert.equal(result, '[RED]:*[RED]:1,1,1');
    });

    it('prints a pointer with no parents', () => {
      const pointer = new GraphPointer(
        new GraphNode(new RuleRef(100), { stackId: 1, pathId: 1, stepId: 1 }),
      );
      assert.equal(printGraphPointer(pointer)({ colorize: mockColorize }), '[RED]:*');
    });
  });

  describe('printGraphNode', () => {
    it('prints a graph node with a character rule', () => {
      const mockNode = createMockNode('1', new RuleChar([65]));
      const result = printGraphNode(mockNode)({
        colorize: mockColorize,
        showPosition: false,
      });
      assert.equal(result, '[GRAY]:[[YELLOW]:A[GRAY]:]');
    });

    it('prints a graph node with a rule reference', () => {
      const mockNode = createMockNode('1', new RuleRef(200));
      const result = printGraphNode(mockNode)({
        colorize: mockColorize,
        showPosition: true,
      });
      assert.equal(result, '[BLUE]:{[GRAY]:1[BLUE]:}[GRAY]:Ref([GREEN]:200[GRAY]:)');
    });

    it('prints a graph node with an end rule', () => {
      const mockNode = createMockNode('1', new RuleEnd());
      const result = printGraphNode(mockNode)({ colorize: mockColorize });
      assert.equal(result, '[YELLOW]:RuleEnd');
    });

    it('renders ranges and escapes newlines', () => {
      const mockNode = createMockNode('1', new RuleChar([[97, 99], 10]));
      const result = printGraphNode(mockNode)({ colorize: mockColorize });
      assert.equal(result, '[GRAY]:[[YELLOW]:[YELLOW]:a[YELLOW]:c\\n[GRAY]:]');
    });

    it('follows the next node with a gray arrow', () => {
      const next = createMockNode('2', new RuleEnd());
      const mockNode = createMockNode('1', new RuleChar([65]), next);
      const result = printGraphNode(mockNode)({ colorize: mockColorize });
      assert.equal(result, '[GRAY]:[[YELLOW]:A[GRAY]:][GRAY]:-> Node(2)');
    });
  });
});

// Keep the Color map honest: every color used by print must be a known code.
describe('Color', () => {
  it('exposes the ANSI codes the printer uses', () => {
    assert.deepStrictEqual(Object.keys(COLORS).sort(), Object.values(Color).sort());
  });
});
