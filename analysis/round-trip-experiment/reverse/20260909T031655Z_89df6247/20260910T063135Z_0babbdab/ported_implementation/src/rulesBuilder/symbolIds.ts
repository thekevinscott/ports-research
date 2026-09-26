/** Bidirectional name <-> id map that also remembers where each name was seen. */
export class SymbolIds {
  // we don't need to delete, just preserve relationships
  private readonly map = new Map<string, number>();
  private readonly positions = new Map<string, number>();
  private readonly reverseMap = new Map<number, string>();

  public get size(): number {
    return this.map.size;
  }

  public keys(): string[] {
    return [...this.map.keys()];
  }

  public has(key: string): boolean {
    return this.map.has(key);
  }

  public get(key: string): number {
    if (!this.map.has(key)) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return this.map.get(key) as number;
  }

  public reverseGet(key: number): string {
    if (!this.reverseMap.has(key)) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return this.reverseMap.get(key) as string;
  }

  public getPos(key: string): number {
    if (!this.positions.has(key)) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return this.positions.get(key) as number;
  }

  public set(key: string, value: number, pos: number): void {
    this.map.set(key, value);
    this.positions.set(key, pos);
    this.reverseMap.set(value, key);
  }

  public [Symbol.iterator](): IterableIterator<[string, number]> {
    return [...this.map.entries()][Symbol.iterator]();
  }
}
