FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# ---- Install dependencies ----
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# ---- Copy full source code ----
COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Put venv at front of PATH
ENV PATH="/app/.venv/bin:$PATH"

# ---- Fix permissions so nonroot can use venv ----
RUN chown -R nonroot:nonroot /app

USER nonroot

ENTRYPOINT ["uv", "run", "main.py"]