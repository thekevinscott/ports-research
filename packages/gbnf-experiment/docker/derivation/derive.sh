#!/bin/sh
set -e

derive() {
  upstream="$1"
  language="$2"
  mkdir -p "/derivation-output/source/${language}"
  git -C /repository archive HEAD "packages/gbnf/${upstream}" \
    | tar -x -C "/derivation-output/source/${language}" --strip-components=3

  node --no-warnings ../../test-writer/dist/test-writer.mjs \
    --testDir ../test \
    --targetDir "/derivation-output/tests/${language}" \
    --language "${upstream}"

  # After the writer, which prunes files it did not write.
  cp -r "/scaffolding/${language}/." "/derivation-output/tests/${language}/"
}

derive javascript typescript
derive python python

cp -r ../test/iteration/grammars /derivation-output/tests/python/iteration/grammars
