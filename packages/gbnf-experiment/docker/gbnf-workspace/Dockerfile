ARG AGENT_IMAGE=agent-harness-sandbox-claude:latest

FROM node:22.19.0-slim@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90 AS prepare

RUN apt-get update
RUN apt-get install -y --no-install-recommends git ca-certificates
RUN npm install -g pnpm@9.4.0

ARG GBNF_COMMIT

WORKDIR /repository
# The pin, not the branch tip, is what makes the prepared corpus reproducible,
# so fetch it by SHA: the layer then busts when the pin moves.
RUN git init -q .
RUN git remote add origin https://github.com/thekevinscott/gbnf
RUN git fetch --depth 1 origin ${GBNF_COMMIT}
RUN git checkout ${GBNF_COMMIT}

COPY patches/ /tmp/patches/
RUN git apply /tmp/patches/*.patch

RUN pnpm install --frozen-lockfile
RUN pnpm --dir packages/test-writer build

RUN cd packages/test-writer && node -e "import('pyodide').then(async ({ loadPyodide }) => { const pyodide = await loadPyodide(); await pyodide.loadPackage('micropip'); await pyodide.pyimport('micropip').install(['black==26.5.1']); })"

WORKDIR /repository/packages/gbnf/javascript

COPY scaffolding/ /scaffolding/
COPY prepare.sh /prepare.sh
RUN /bin/sh /prepare.sh

# Every file the host may pick from. The host selects; nothing in here does.
RUN find /prepared -type f -printf '%P\n' | sort > /prepared.list

FROM prepare AS selected

# One line per file, relative to /prepared, chosen on the host. Only this layer
# varies with the choice, so each distinct list is its own cached layer.
ARG FILES
RUN mkdir /selected && printf '%s\n' "$FILES" | tar -C /prepared -cf - -T - | tar -xf - -C /selected

FROM ${AGENT_IMAGE}

# Root-owned under the agent's uid: readable, not writable.
COPY --from=selected /selected/ /workspace/
