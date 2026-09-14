FROM node:24.20.0-slim

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
