export class SymbolIds {
  private __map__: Map<string, number>;
  private __pos__: Map<string, number>;
  private __reverseMap__: Map<number, string>;

  constructor() {
    this.__map__ = new Map();
    this.__pos__ = new Map();
    this.__reverseMap__ = new Map();
  }

  entries(): IterableIterator<[string, number]> {
    return this.__map__.entries();
  }

  items(): IterableIterator<[string, number]> {
    return this.entries();
  }

  keys(): IterableIterator<string> {
    return this.__map__.keys();
  }

  values(): IterableIterator<number> {
    return this.__map__.values();
  }

  [Symbol.iterator](): IterableIterator<[string, number]> {
    return this.entries();
  }

  get size(): number {
    return this.__map__.size;
  }

  get(key: string): number | undefined {
    return this.__map__.get(key);
  }

  set(key: string, value: number, pos: number): void {
    this.__map__.set(key, value);
    this.__reverseMap__.set(value, key);
    this.__pos__.set(key, pos);
  }

  has(key: string): boolean {
    return this.__map__.has(key);
  }

  reverseGet(key: number): string {
    const val = this.__reverseMap__.get(key);
    if (val === undefined) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return val;
  }

  getPos(key: string): number {
    const val = this.__pos__.get(key);
    if (val === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return val;
  }

  reverse_get(key: number): string {
    return this.reverseGet(key);
  }

  get_pos(key: string): number {
    return this.getPos(key);
  }

  toJSON(): Record<string, number> {
    return Object.fromEntries(this.__map__.entries());
  }
}
