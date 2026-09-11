export enum Color {
  BLUE = '\x1b[34m',
  CYAN = '\x1b[36m',
  GREEN = '\x1b[32m',
  RED = '\x1b[31m',
  GRAY = '\x1b[90m',
  YELLOW = '\x1b[33m',
}

export type Colorize = (value: string | number, color?: Color) => string;

export const colorize: Colorize = (value, color) => `${color}${value}`;

export const noColor: Colorize = (value) => `${value}`;
