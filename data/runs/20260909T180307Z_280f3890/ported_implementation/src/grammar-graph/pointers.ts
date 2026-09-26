import type { GraphPointer } from './graph-pointer.js';

/**
 * An insertion-ordered collection of pointers, keyed by pointer id.
 *
 * A pointer's id is the sum of its node's id and its parent's id chain, so two
 * pointers sharing an id point at the same node through an identical parent
 * chain and are interchangeable when walking the graph.
 */
export class Pointers {
  readonly #pointers = new Map<string, GraphPointer>();

  constructor(...pointers: GraphPointer[]) {
    for (const pointer of pointers) {
      this.add(pointer);
    }
  }

  add(pointer: GraphPointer): void {
    this.#pointers.set(pointer.id, pointer);
  }

  *[Symbol.iterator](): Generator<GraphPointer> {
    yield* this.#pointers.values();
  }

  get size(): number {
    return this.#pointers.size;
  }
}
