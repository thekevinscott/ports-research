/**
 * Port of `gbnf/grammar_graph/generic_set.py`.
 *
 * A `Map` keyed by a derived key, paired with a `Set` keyed by object identity.
 */

export class GenericSet<T, K> {
  #keys = new Map<K, T>();
  #set = new Set<T>();

  constructor(public getKey: (el: T) => K) {}

  add(el: T): void {
    const key = this.getKey(el);
    if (!this.#keys.has(key)) {
      this.#keys.set(key, el);
      this.#set.add(el);
    }
  }

  delete(el: T): void {
    const key = this.getKey(el);
    const ref = this.#keys.get(key);
    if (ref === undefined) {
      throw new Error('Could not get ref');
    }
    this.#keys.delete(key);
    this.#set.delete(ref);
  }

  has(el: T): boolean {
    return this.#set.has(el);
  }

  get(el: T): T | undefined {
    return this.#keys.get(this.getKey(el));
  }

  *[Symbol.iterator](): IterableIterator<T> {
    yield* [...this.#set];
  }

  get size(): number {
    return this.#set.size;
  }
}
