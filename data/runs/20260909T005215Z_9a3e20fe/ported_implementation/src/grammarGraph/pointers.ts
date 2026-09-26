import type { GraphPointer } from './graphPointer.ts';

/**
 * An insertion-ordered, id-deduplicated collection of pointers. Two pointers
 * that share an id address the same node through the same parent chain, so
 * only one of them needs to be walked.
 */
export class Pointers {
  #pointers = new Map<string, GraphPointer>();

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
