import type { GraphPointer } from './graph-pointer.ts';

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

  *[Symbol.iterator](): IterableIterator<GraphPointer> {
    yield* this.#pointers.values();
  }

  get size(): number {
    return this.#pointers.size;
  }
}
