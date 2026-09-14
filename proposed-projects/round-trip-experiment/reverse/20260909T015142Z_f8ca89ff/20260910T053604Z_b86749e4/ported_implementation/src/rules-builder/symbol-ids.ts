export class SymbolIds {
  // we don't need to delete, just preserve relationships
  private map = new Map<string, number>();
  private pos = new Map<string, number>();
  private reverseMap = new Map<number, string>();

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
    const value = this.map.get(key);
    if (value === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return value;
  }

  public reverseGet(key: number): string {
    const value = this.reverseMap.get(key);
    if (value === undefined) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return value;
  }

  public getPos(key: string): number {
    const value = this.pos.get(key);
    if (value === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return value;
  }

  public set(key: string, value: number, pos: number): void {
    this.map.set(key, value);
    this.pos.set(key, pos);
    this.reverseMap.set(value, key);
  }

  public *[Symbol.iterator](): Generator<[string, number]> {
    yield* this.map.entries();
  }
}
