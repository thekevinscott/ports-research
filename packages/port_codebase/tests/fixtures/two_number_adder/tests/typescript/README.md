# Generated TypeScript test suite

Copy the suite and its config into the ported implementation, then run it:

```sh
cd /workspace/ported_implementation
cp -r /workspace/tests/typescript tests
cp tests/vitest.config.unit.ts .
npx vitest run --config vitest.config.unit.ts
```

The config aliases `two_number_adder` to `/workspace/ported_implementation/src/index.ts`.
Repoint it if your entry file differs.
