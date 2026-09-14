import { GenericSet } from './generic-set.js';
import type { GraphPointer } from './graph-pointer.js';

/**
 * A pointer's id is the sum of its node's id and its parent's id chain, so a
 * set keyed by id keeps exactly one pointer per distinct position in the graph.
 */
export type Pointers = GenericSet<GraphPointer, string>;

export const makePointers = (): Pointers =>
  new GenericSet<GraphPointer, string>(pointer => pointer.id);
