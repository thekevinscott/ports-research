# Numbered steps follow the porting pipeline note (PR #71), gbnf-experiment half.
FROM node:22.19.0-slim@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90

RUN apt-get update
RUN apt-get install -y --no-install-recommends git ca-certificates rsync make
RUN npm install -g pnpm@9.4.0

ARG GBNF_COMMIT

WORKDIR /repository
# 1. Clone gbnf at the pinned commit.
RUN git init -q .
RUN git remote add origin https://github.com/thekevinscott/gbnf
RUN git fetch --depth 1 origin ${GBNF_COMMIT}
RUN git checkout ${GBNF_COMMIT}

# 2. Apply patches.
COPY patches/ /tmp/patches/
RUN git apply /tmp/patches/*.patch

# 3. Install node modules and build test-writer.
RUN pnpm install --frozen-lockfile
RUN pnpm --dir packages/test-writer build
# pnpm skipped the write-tests bin at install time because test-writer's dist did not exist yet.
RUN pnpm install --frozen-lockfile --offline

# 4. Run test-writer

# Generate integration tests for typescript
RUN pnpm --filter gbnf test:integration:write
# Generate integration tests for python
RUN cd packages/gbnf/python && make write_integration_tests && cd -

# Everything above is shared by all sixteen images; only the copies below vary.
ARG SOURCE_LANGUAGE
ARG INCLUDE_UNIT_TESTS=false
ARG INCLUDE_PYTHON_TESTS=false
ARG INCLUDE_TYPESCRIPT_TESTS=false

COPY reference-filters/ /reference-filters/

# 5. /reference/source/<lang>: the source package in its upstream layout,
#    filtered on the way in. The flags prepend the rules that let its colocated
#    unit tests and its generated integration suite through.
RUN case "${SOURCE_LANGUAGE}" in \
      python) upstream=python; integration="${INCLUDE_PYTHON_TESTS}" ;; \
      typescript) upstream=javascript; integration="${INCLUDE_TYPESCRIPT_TESTS}" ;; \
      *) echo "SOURCE_LANGUAGE must be python or typescript" >&2; exit 1 ;; \
    esac \
 && cd "/reference-filters/${SOURCE_LANGUAGE}" \
 && { [ "${INCLUDE_UNIT_TESTS}" != "true" ] || cat unit-tests.rules; \
      [ "${integration}" != "true" ] || cat integration-tests.rules; \
      cat source.rules; } > /tmp/source.rules \
 && mkdir -p "/reference/source/${SOURCE_LANGUAGE}" \
 && rsync -a --prune-empty-dirs --filter="merge /tmp/source.rules" \
      "/repository/packages/gbnf/${upstream}/" "/reference/source/${SOURCE_LANGUAGE}/"

# 6. /reference/target/<lang>: the other language's generated integration suite
#    in its upstream layout, with the files upstream runs it with and no source.
RUN case "${SOURCE_LANGUAGE}" in \
      python) target=typescript; upstream=javascript; integration="${INCLUDE_TYPESCRIPT_TESTS}" ;; \
      typescript) target=python; upstream=python; integration="${INCLUDE_PYTHON_TESTS}" ;; \
    esac \
 && if [ "${integration}" = "true" ]; then \
      cat "/reference-filters/${target}/integration-tests.rules" \
          "/reference-filters/${target}/harness.rules" > /tmp/target.rules \
      && mkdir -p "/reference/target/${target}" \
      && rsync -a --prune-empty-dirs --filter="merge /tmp/target.rules" \
           "/repository/packages/gbnf/${upstream}/" "/reference/target/${target}/"; \
    fi
