/**
 * A set keyed by a derived key, but holding (and comparing) elements by reference.
 *
 * The key map decides what counts as a duplicate on the way in; the set half
 * answers membership by reference.
 */
export class GenericSet<T, K> {
  #getKey: (el: T) => K;
  #keys = new Map<K, T>();
  #set = new Set<T>();

  constructor(getKey: (el: T) => K) {
    this.#getKey = getKey;
  }

  add(el: T): void {
    const key = this.#getKey(el);
    if (!this.#keys.has(key)) {
      this.#keys.set(key, el);
      this.#set.add(el);
    }
  }

  delete(el: T): void {
    const key = this.#getKey(el);
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
    return this.#keys.get(this.#getKey(el));
  }

  get size(): number {
    return this.#set.size;
  }

  *[Symbol.iterator](): Generator<T> {
    yield* [...this.#set];
  }
}
