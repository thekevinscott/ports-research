export class SymbolIds {
  // we don't need to delete, just preserve relationships
  private _map = new Map<string, number>();
  private _pos = new Map<string, number>();
  private _reverseMap = new Map<number, string>();

  get size(): number {
    return this._map.size;
  }

  keys(): string[] {
    return [...this._map.keys()];
  }

  has(key: string): boolean {
    return this._map.has(key);
  }

  get(key: string): number {
    const value = this._map.get(key);
    if (value === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return value;
  }

  reverseGet(key: number): string {
    const value = this._reverseMap.get(key);
    if (value === undefined) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return value;
  }

  getPos(key: string): number {
    const pos = this._pos.get(key);
    if (pos === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return pos;
  }

  set(key: string, value: number, pos: number): void {
    this._map.set(key, value);
    this._pos.set(key, pos);
    this._reverseMap.set(value, key);
  }

  *[Symbol.iterator](): IterableIterator<[string, number]> {
    yield* this._map.entries();
  }
}
