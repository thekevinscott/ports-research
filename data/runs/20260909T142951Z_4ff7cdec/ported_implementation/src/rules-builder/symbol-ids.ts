export class SymbolIds {
  #map = new Map<string, number>();
  #pos = new Map<string, number>();
  #reverseMap = new Map<number, string>();

  entries(): IterableIterator<[string, number]> {
    return this.#map.entries();
  }

  [Symbol.iterator](): IterableIterator<[string, number]> {
    return this.#map.entries();
  }

  get size(): number {
    return this.#map.size;
  }

  get(key: string): number | undefined {
    return this.#map.get(key);
  }

  set(key: string, value: number, pos: number): void {
    this.#map.set(key, value);
    this.#reverseMap.set(value, key);
    this.#pos.set(key, pos);
  }

  has(key: string): boolean {
    return this.#map.has(key);
  }

  reverseGet(key: number): string {
    const value = this.#reverseMap.get(key);
    if (value === undefined) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return value;
  }

  getPos(key: string): number {
    const value = this.#pos.get(key);
    if (value === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return value;
  }
}
