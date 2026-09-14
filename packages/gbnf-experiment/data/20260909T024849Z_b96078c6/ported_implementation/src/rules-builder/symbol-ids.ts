/**
 * A `Map` of rule name -> rule id, that additionally remembers the position in the
 * grammar each symbol was declared at, and supports looking a name up by its id.
 */
export class SymbolIds extends Map<string, number> {
  // Lazily created: `Map`'s constructor may call `set` before field initialisers run.
  declare positions: Map<string, number> | undefined;
  declare reverseMapping: Map<number, string> | undefined;

  set(key: string, value: number, pos = 0): this {
    super.set(key, value);
    (this.reverseMapping ??= new Map()).set(value, key);
    (this.positions ??= new Map()).set(key, pos);
    return this;
  }

  /** Alias of `entries()`, mirroring the reference implementation. */
  items(): IterableIterator<[string, number]> {
    return this.entries();
  }

  reverseGet(key: number): string {
    const val = this.reverseMapping?.get(key);
    if (val === undefined) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return val;
  }

  getPos(key: string): number {
    const val = this.positions?.get(key);
    if (val === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return val;
  }

  toJSON(): Record<string, number> {
    return Object.fromEntries(this.entries());
  }
}
