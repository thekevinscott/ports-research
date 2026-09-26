/** A set keyed by a derived value; first element to claim a key wins. */
export class GenericSet<T, K> {
  private readonly getKey: (el: T) => K;
  private readonly keys = new Map<K, T>();

  public constructor(getKey: (el: T) => K) {
    this.getKey = getKey;
  }

  public add(el: T): void {
    const key = this.getKey(el);
    if (!this.keys.has(key)) {
      this.keys.set(key, el);
    }
  }

  public delete(el: T): void {
    const key = this.getKey(el);
    if (!this.keys.has(key)) {
      throw new Error('Could not get ref');
    }
    this.keys.delete(key);
  }

  public has(el: T): boolean {
    for (const existing of this.keys.values()) {
      if (existing === el) {
        return true;
      }
    }
    return false;
  }

  public get(el: T): T | undefined {
    return this.keys.get(this.getKey(el));
  }

  public [Symbol.iterator](): IterableIterator<T> {
    return [...this.keys.values()][Symbol.iterator]();
  }

  public get size(): number {
    return this.keys.size;
  }
}
