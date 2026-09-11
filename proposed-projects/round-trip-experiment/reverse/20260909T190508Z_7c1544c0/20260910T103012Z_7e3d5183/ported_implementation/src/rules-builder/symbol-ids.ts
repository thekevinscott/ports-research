/**
 * An insertion-ordered, bidirectional name <-> id map.
 *
 * We never need to delete, just to preserve relationships.
 */
export class SymbolIds {
  private map = new Map<string, number>();
  private posMap = new Map<string, number>();
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
    if (!this.map.has(key)) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return this.map.get(key) as number;
  }

  reverseGet(key: number): string {
    if (!this.reverseMap.has(key)) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return this.reverseMap.get(key) as string;
  }

  getPos(key: string): number {
    if (!this.posMap.has(key)) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return this.posMap.get(key) as number;
  }

  set(key: string, value: number, pos: number): void {
    this.map.set(key, value);
    this.posMap.set(key, pos);
    this.reverseMap.set(value, key);
  }

  [Symbol.iterator](): IterableIterator<[string, number]> {
    return this.map.entries();
  }
}
