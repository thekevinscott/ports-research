FROM botbox-claude:latest

USER root

COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /uvx /usr/local/bin/
ENV UV_PYTHON_INSTALL_DIR=/usr/local/share/uv/python \
    UV_PYTHON_BIN_DIR=/usr/local/bin \
    UV_TOOL_DIR=/usr/local/share/uv/tools \
    UV_TOOL_BIN_DIR=/usr/local/bin
RUN uv python install --preview-features python-install-default --default 3.14.3
RUN uv tool install --python 3.14.3 pytest==9.1.1 --with pytest-describe==3.2.0

RUN npm install -g vitest@2.1.3
RUN npm install -g pnpm@9.4.0
ENV NODE_PATH=/usr/local/lib/node_modules

USER node
