#!/bin/sh
set -e

prepare() {
  upstream="$1"
  language="$2"
  mkdir -p "/prepared/source/${language}"
  git -C /repository archive HEAD "packages/gbnf/${upstream}" \
    | tar -x -C "/prepared/source/${language}" --strip-components=3

  node --no-warnings ../../test-writer/dist/test-writer.mjs \
    --testDir ../test \
    --targetDir "/prepared/tests/${language}" \
    --language "${upstream}"
}

prepare javascript typescript
prepare python python

cp -r ../test/iteration/grammars /prepared/tests/python/iteration/grammars
# After the writer, which prunes files it did not write.
cp -r /scaffolding/. /prepared/tests/
