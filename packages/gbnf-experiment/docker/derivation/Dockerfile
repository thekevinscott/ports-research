FROM node:22.19.0-slim@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90

RUN apt-get update
RUN apt-get install -y --no-install-recommends git ca-certificates
RUN npm install -g pnpm@9.4.0

ARG GBNF_COMMIT

WORKDIR /repository
# The pin, not the branch tip, is what makes the derived corpus reproducible,
# so fetch it by SHA: the layer then busts when the pin moves.
RUN git init -q .
RUN git remote add origin https://github.com/thekevinscott/gbnf
RUN git fetch --depth 1 origin ${GBNF_COMMIT}
RUN git checkout ${GBNF_COMMIT}

COPY patches/ /tmp/patches/
RUN git apply /tmp/patches/*.patch

RUN git config --system --add safe.directory /repository

RUN pnpm install --frozen-lockfile
RUN pnpm --dir packages/test-writer build

RUN cd packages/test-writer && node -e "import('pyodide').then(async ({ loadPyodide }) => { const pyodide = await loadPyodide(); await pyodide.loadPackage('micropip'); await pyodide.pyimport('micropip').install(['black==26.5.1']); })"

# After the build steps above, so the runtime host uid finds nothing already there root-owned.
ENV HOME=/tmp/derivation-home \
    XDG_DATA_HOME=/tmp/derivation-home/.local/share \
    XDG_CACHE_HOME=/tmp/derivation-home/.cache

WORKDIR /repository/packages/gbnf/javascript

COPY scaffolding/ /scaffolding/
COPY derive.sh /derive.sh
CMD ["/bin/sh", "/derive.sh"]
