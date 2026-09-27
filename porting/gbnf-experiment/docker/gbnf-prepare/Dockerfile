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

# Everything above is shared by all eight images; only the copies below vary.
ARG SOURCE_LANGUAGE
ARG INCLUDE_PYTHON_TESTS=false
ARG INCLUDE_TYPESCRIPT_TESTS=false


### BELOW THIS LINE NEEDS UPDATING




RUN if [ "${INCLUDE_PYTHON_TESTS}" = "true" ]; then \
      mkdir -p /reference/tests && cp -r /tmp/tests/python /reference/tests/python; \
    fi
RUN if [ "${INCLUDE_TYPESCRIPT_TESTS}" = "true" ]; then \
      mkdir -p /reference/tests && cp -r /tmp/tests/typescript /reference/tests/typescript; \
    fi

# 5. Copy the source language into /reference/source, filtered during the copy.
COPY reference-filters/ /reference-filters/
RUN case "${SOURCE_LANGUAGE}" in \
      python) upstream=python ;; \
      typescript) upstream=javascript ;; \
      *) echo "SOURCE_LANGUAGE must be python or typescript" >&2; exit 1 ;; \
    esac \
    && mkdir -p /reference/source \
    && rsync -a --prune-empty-dirs \
         --filter="merge /reference-filters/${SOURCE_LANGUAGE}.rules" \
         "/repository/packages/gbnf/${upstream}/" /reference/source/
# 6. (clean up build litter) has nothing to do: only what steps 4 and 5 place
# reaches /reference.
