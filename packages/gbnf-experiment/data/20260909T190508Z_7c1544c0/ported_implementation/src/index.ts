/**
 * TypeScript entry point for the Python implementation in `../gbnf`.
 *
 * The generated test suite (`tests/`) is written in TypeScript and imports
 * `gbnf`, so this module exposes the reference API and forwards every call to
 * `../bridge/server.py` over a pair of FIFOs. It deliberately contains no
 * grammar logic: rules, error messages and positions all come from Python.
 */
import { spawn, execFileSync, type ChildProcess } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SERVER = path.join(HERE, '..', 'bridge', 'server.py');
const PYTHON = process.env.GBNF_PYTHON ?? 'python3';

export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

export type Range = [number, number];
export interface RuleChar {
  type: RuleType.CHAR;
  value: (number | Range)[];
}
export interface RuleCharExclude {
  type: RuleType.CHAR_EXCLUDE;
  value: (number | Range)[];
}
export interface RuleEnd {
  type: RuleType.END;
}
export type Rule = RuleChar | RuleCharExclude | RuleEnd;
export type ValidInput = string | number | number[];

export const isRange = (range?: unknown): range is Range =>
  Array.isArray(range) && range.length === 2 && range.every((n) => typeof n === 'number');

interface Response {
  id: number;
  ok: boolean;
  state?: number;
  rules?: Rule[];
  size?: number;
  grammar?: string;
  message?: string;
  src?: string;
  errorForMostRecentInput?: string;
  error?: { name: string; message: string; args?: [ValidInput, number, ValidInput] };
}

class Bridge {
  #child?: ChildProcess;
  #requestFd?: number;
  #responseFd?: number;
  #dir?: string;
  #buffer = '';
  #nextId = 0;
  #pending = Buffer.alloc(1 << 16);

  #start() {
    // fail loudly here rather than deadlocking on a FIFO the server never opens
    execFileSync(PYTHON, [SERVER, '--check'], { timeout: 30000, stdio: 'pipe' });

    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'gbnf-bridge-'));
    const requestPath = path.join(dir, 'requests');
    const responsePath = path.join(dir, 'responses');
    execFileSync('mkfifo', [requestPath, responsePath]);

    const child = spawn(PYTHON, [SERVER, requestPath, responsePath], {
      stdio: ['ignore', 'inherit', 'inherit'],
    });
    child.on('error', (err) => {
      throw err;
    });

    // Opening a FIFO blocks until the other end opens it; the server opens the
    // request FIFO first, so we must do the same.
    this.#requestFd = fs.openSync(requestPath, 'w');
    this.#responseFd = fs.openSync(responsePath, 'r');
    this.#child = child;
    this.#dir = dir;

    process.on('exit', () => this.#stop());
  }

  #stop() {
    try {
      if (this.#requestFd !== undefined) fs.closeSync(this.#requestFd);
      if (this.#responseFd !== undefined) fs.closeSync(this.#responseFd);
      this.#child?.kill();
      if (this.#dir) fs.rmSync(this.#dir, { recursive: true, force: true });
    } catch {
      // the process is going away regardless
    }
    this.#requestFd = undefined;
    this.#responseFd = undefined;
    this.#child = undefined;
    this.#dir = undefined;
  }

  request(payload: Record<string, unknown>): Response {
    if (this.#child === undefined) {
      this.#start();
    }
    const id = this.#nextId++;
    fs.writeSync(this.#requestFd!, `${JSON.stringify({ ...payload, id })}\n`);

    let newline = this.#buffer.indexOf('\n');
    while (newline === -1) {
      const read = fs.readSync(this.#responseFd!, this.#pending, 0, this.#pending.length, null);
      if (read === 0) {
        throw new Error('The gbnf bridge process exited unexpectedly');
      }
      this.#buffer += this.#pending.toString('utf8', 0, read);
      newline = this.#buffer.indexOf('\n');
    }
    const line = this.#buffer.slice(0, newline);
    this.#buffer = this.#buffer.slice(newline + 1);

    const response = JSON.parse(line) as Response;
    if (response.id !== id) {
      throw new Error(`Out of order response: expected ${id}, got ${response.id}`);
    }
    if (response.ok === false) {
      throw toError(response.error!);
    }
    return response;
  }
}

const bridge = new Bridge();

const toError = (error: { name: string; message: string; args?: [ValidInput, number, ValidInput] }) => {
  if (error.name === 'InputParseError' && error.args) {
    return new InputParseError(...error.args);
  }
  if (error.name === 'GrammarParseError' && error.args) {
    const [grammar, pos, reason] = error.args as unknown as [string, number, string];
    return new GrammarParseError(grammar, pos, reason);
  }
  return new Error(error.message);
};

export class GrammarParseError extends Error {
  grammar: string;
  pos: number;
  reason: string;
  constructor(grammar: string, pos: number, reason: string) {
    super(bridge.request({ op: 'grammar_error', grammar, pos, reason }).message);
    this.name = 'GrammarParseError';
    this.grammar = grammar;
    this.pos = pos;
    this.reason = reason;
  }
}

export class InputParseError extends Error {
  src: string;
  errorForMostRecentInput: string;
  constructor(mostRecentInput: ValidInput, pos: number, previousInput: ValidInput = '') {
    const response = bridge.request({
      op: 'input_error',
      mostRecentInput,
      pos,
      previousInput,
    });
    super(response.message);
    this.name = 'InputParseError';
    this.src = response.src!;
    this.errorForMostRecentInput = response.errorForMostRecentInput!;
  }
}

export class ParseState {
  #state: number;
  #rules: Rule[];

  constructor(state: number, rules: Rule[]) {
    this.#state = state;
    this.#rules = rules;
  }

  *[Symbol.iterator](): IterableIterator<Rule> {
    yield* this.#rules;
  }

  *rules(): IterableIterator<Rule> {
    yield* this.#rules;
  }

  add(input: ValidInput): ParseState {
    const { state, rules } = bridge.request({ op: 'add', state: this.#state, input });
    return new ParseState(state!, rules!);
  }

  get size(): number {
    return this.#rules.length;
  }

  get grammar(): string {
    return bridge.request({ op: 'grammar', state: this.#state }).grammar!;
  }
}

export const GBNF = (input: string, initialString: ValidInput = ''): ParseState => {
  const { state, rules } = bridge.request({
    op: 'create',
    grammar: input,
    input: initialString,
  });
  return new ParseState(state!, rules!);
};

export default GBNF;
