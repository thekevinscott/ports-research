export class GenericSet<T, K> {
  private getKey: (el: T) => K;
  private keys = new Map<K, T>();

  constructor(getKey: (el: T) => K) {
    this.getKey = getKey;
  }

  add(el: T): void {
    const key = this.getKey(el);
    if (!this.keys.has(key)) {
      this.keys.set(key, el);
    }
  }

  delete(el: T): void {
    const key = this.getKey(el);
    if (!this.keys.has(key)) {
      throw new Error('Could not get ref');
    }
    this.keys.delete(key);
  }

  has(el: T): boolean {
    return this.keys.has(this.getKey(el));
  }

  get(el: T): T | undefined {
    return this.keys.get(this.getKey(el));
  }

  get size(): number {
    return this.keys.size;
  }

  *[Symbol.iterator](): IterableIterator<T> {
    yield* [...this.keys.values()];
  }
}
