export enum Color {
  BLUE = '\x1b[34m',
  CYAN = '\x1b[36m',
  GREEN = '\x1b[32m',
  RED = '\x1b[31m',
  GRAY = '\x1b[90m',
  YELLOW = '\x1b[33m',
}

export type Colorize = (value: unknown, color?: Color) => string;

export const colorize: Colorize = (value, color) => `${color}${value}`;

/** Drop-in for `colorize` that ignores the requested color. */
export const noColor: Colorize = (value) => `${value}`;
