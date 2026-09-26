// we don't need to delete, just preserve relationships
export class SymbolIds {
  private map = new Map<string, number>();
  private pos = new Map<string, number>();
  private reverseMap = new Map<number, string>();

  get size(): number {
    return this.map.size;
  }

  keys(): IterableIterator<string> {
    return this.map.keys();
  }

  has(key: string): boolean {
    return this.map.has(key);
  }

  get(key: string): number {
    const value = this.map.get(key);
    if (value === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return value;
  }

  reverseGet(key: number): string {
    const value = this.reverseMap.get(key);
    if (value === undefined) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return value;
  }

  getPos(key: string): number {
    const pos = this.pos.get(key);
    if (pos === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return pos;
  }

  set(key: string, value: number, pos: number): void {
    this.map.set(key, value);
    this.pos.set(key, pos);
    this.reverseMap.set(value, key);
  }

  *[Symbol.iterator](): IterableIterator<[string, number]> {
    yield* [...this.map.entries()];
  }
}
