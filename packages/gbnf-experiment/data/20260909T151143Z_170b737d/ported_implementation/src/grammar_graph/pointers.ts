import type { GraphPointer } from "./graph_pointer.ts";

export class Pointers {
  private __pointers__: Map<string, GraphPointer>;

  constructor(...pointers: GraphPointer[]) {
    this.__pointers__ = new Map();
    for (const pointer of pointers) {
      this.add(pointer);
    }
  }

  toString(): string {
    return `<Pointers ${[...this].map((p) => String(p.node.rule)).join(", ")}>`;
  }

  add(pointer: GraphPointer): void {
    this.__pointers__.set(pointer.id, pointer);
  }

  *[Symbol.iterator](): Generator<GraphPointer> {
    yield* this.__pointers__.values();
  }

  get length(): number {
    return this.__pointers__.size;
  }
}
