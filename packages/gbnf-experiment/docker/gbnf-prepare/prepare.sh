#!/bin/sh
set -e

prepare() {
  upstream="$1"
  language="$2"
  mkdir -p "/prepared-output/source/${language}"
  git -C /repository archive HEAD "packages/gbnf/${upstream}" \
    | tar -x -C "/prepared-output/source/${language}" --strip-components=3

  node --no-warnings ../../test-writer/dist/test-writer.mjs \
    --testDir ../test \
    --targetDir "/prepared-output/tests/${language}" \
    --language "${upstream}"

  # After the writer, which prunes files it did not write.
  cp -r "/scaffolding/${language}/." "/prepared-output/tests/${language}/"
}

prepare javascript typescript
prepare python python

cp -r ../test/iteration/grammars /prepared-output/tests/python/iteration/grammars
