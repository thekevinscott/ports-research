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

# Everything above is shared by every condition; only the copies below vary.
# The rules text is composed on the host by
# gbnf_experiment.prepare_filesystem.assemble_whitelist and passed in whole,
# so the image never sees a flag. TARGET_RULES empty means no target folder.
ARG SOURCE_LANGUAGE
ARG SOURCE_RULES
ARG TARGET_LANGUAGE
ARG TARGET_RULES=""

# 5. /shared/source/<lang>: the source package in its upstream layout,
#    filtered by the whitelist.
RUN printf '%s\n' "${SOURCE_RULES}" > /tmp/source.rules && \
    mkdir -p /shared/source && \
    rsync -a --prune-empty-dirs --filter="merge /tmp/source.rules" \
        /repository/packages/gbnf/${SOURCE_LANGUAGE}/ \
        /shared/source/${SOURCE_LANGUAGE}/

# 6. /shared/target/<lang>: the other language's generated integration suite
#    and the files upstream runs it with, no source. Only when asked for.
RUN [ -z "${TARGET_RULES}" ] || { \
        printf '%s\n' "${TARGET_RULES}" > /tmp/target.rules && \
        mkdir -p /shared/target && \
        rsync -a --prune-empty-dirs --filter="merge /tmp/target.rules" \
            /repository/packages/gbnf/${TARGET_LANGUAGE}/ \
            /shared/target/${TARGET_LANGUAGE}/; \
    }
