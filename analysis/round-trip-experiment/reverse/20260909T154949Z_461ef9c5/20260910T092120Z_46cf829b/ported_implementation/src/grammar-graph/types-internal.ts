import type { GenericSet } from './generic-set.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';

/** Nodes of a single rule stack, keyed by path id. */
export type RootNode = Map<number, GraphNode>;

/** A pointer's id is its node id prefixed by its parent chain, so it de-duplicates. */
export type Pointers = GenericSet<GraphPointer, string>;
