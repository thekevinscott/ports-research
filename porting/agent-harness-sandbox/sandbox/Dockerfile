ARG AGENT

FROM node:24.20.0-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /uvx /usr/local/bin/

RUN apt-get update && \
    apt-get install -y --no-install-recommends git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g vitest@2.1.3

ENV NODE_PATH=/usr/local/lib/node_modules

ENV UV_PYTHON_INSTALL_DIR=/usr/local/share/uv/python \
    UV_PYTHON_BIN_DIR=/usr/local/bin \
    UV_TOOL_DIR=/usr/local/share/uv/tools \
    UV_TOOL_BIN_DIR=/usr/local/bin

RUN uv python install --preview-features python-install-default --default 3.14.3

RUN uv tool install --python 3.14.3 pytest==9.1.1 --with pytest-describe==3.2.0

WORKDIR /workspace
RUN chown node:node /workspace

RUN find / -xdev -perm /6000 -type f -exec chmod a-s {} +

USER node

RUN uv run --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 pytest --version


FROM base AS dependencies

USER root

RUN mkdir -p /input && chown node:node /input

# Whatever a caller adds to this stage installs as the user the agent runs as: a
# root-owned tree is not writable by node once it reaches the run stage.
USER node


FROM base AS claude

USER root

RUN npm install -g @anthropic-ai/claude-code@2.1.263

ENV DISABLE_AUTOUPDATER=1 \
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
    CLAUDE_CONFIG_DIR=/home/node/.claude


FROM base AS pi

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends ripgrep fd-find && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/fdfind /usr/local/bin/fd

RUN npm install -g @earendil-works/pi-coding-agent@0.74.0

ENV PI_CODING_AGENT_DIR=/home/node/.pi/agent


FROM ${AGENT}

RUN find / -xdev -perm /6000 -type f -exec chmod a-s {} +

COPY --from=dependencies --chown=node:node /input /input

USER node
