// Copies the reference TypeScript sources into .work/ref-src and marks type-only
// import specifiers with the `type` keyword, so node's --experimental-transform-types
// (which has no type information and cannot elide them on its own) can load them.
// Only import statements are rewritten; no runtime code is altered.
import {
  cpSync,
  existsSync,
  readdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { dirname, join, resolve as resolvePath } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = process.env.REFERENCE_SRC ?? '/workspace/reference_implementation/src';
const DST = join(HERE, '.work', 'ref-src');

rmSync(DST, { recursive: true, force: true });
cpSync(SRC, DST, { recursive: true });

const walk = (dir) =>
  readdirSync(dir).flatMap((entry) => {
    const full = join(dir, entry);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });

const files = walk(DST).filter((f) => f.endsWith('.ts') && !f.endsWith('.test.ts'));

const runtimeExports = (file) => {
  if (!existsSync(file)) {
    return null;
  }
  const src = readFileSync(file, 'utf-8');
  const names = new Set();
  const declared =
    /export\s+(?:declare\s+)?(?:abstract\s+)?(?:class|const|let|var|function|enum)\s+(\w+)/g;
  for (const match of src.matchAll(declared)) {
    names.add(match[1]);
  }
  for (const match of src.matchAll(/export\s*\{([^}]*)\}/g)) {
    for (const part of match[1].split(',')) {
      const cleaned = part.trim();
      if (!cleaned || cleaned.startsWith('type ')) {
        continue;
      }
      const name = cleaned.split(/\s+as\s+/)[0].trim();
      if (name) {
        names.add(name);
      }
    }
  }
  return names;
};

for (const file of files) {
  const src = readFileSync(file, 'utf-8').replace(
    /import\s*\{([\s\S]*?)\}\s*from\s*['"]([^'"]+)['"]/g,
    (whole, specifiers, from) => {
      if (!from.startsWith('.')) {
        return whole;
      }
      const target = resolvePath(dirname(file), from.replace(/\.js$/, '.ts'));
      const exported = runtimeExports(target);
      if (exported === null) {
        return whole;
      }
      const patched = specifiers
        .split(',')
        .map((raw) => {
          const trimmed = raw.trim();
          if (!trimmed || trimmed.startsWith('type ')) {
            return raw;
          }
          const name = trimmed.split(/\s+as\s+/)[0].trim();
          return exported.has(name) ? raw : raw.replace(name, `type ${name}`);
        })
        .join(',');
      return `import {${patched}} from '${from}'`;
    },
  );
  writeFileSync(file, src);
}

console.log(`prepared ${files.length} reference files in ${DST}`);
