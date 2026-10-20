FROM botbox-claude:latest

USER root

COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /uvx /usr/local/bin/
ENV UV_PYTHON_INSTALL_DIR=/usr/local/share/uv/python \
    UV_PYTHON_BIN_DIR=/usr/local/bin
RUN uv python install --preview-features python-install-default --default 3.14.3
RUN uv pip install --system --break-system-packages --python 3.14.3 pytest==9.1.1 pytest-describe==3.2.0 \
    && ln -s "$(dirname "$(uv python find 3.14.3)")/pytest" /usr/local/bin/pytest

RUN npm install -g vitest@2.1.3
RUN npm install -g pnpm@9.4.0
ENV NODE_PATH=/usr/local/lib/node_modules
# ESM resolution ignores NODE_PATH but walks up to /node_modules.
RUN mkdir /node_modules \
    && for package in /usr/local/lib/node_modules/*; do ln -s "$package" /node_modules/; done \
    && chown user /node_modules

USER user
