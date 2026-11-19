# Montaj studiyasi (AP-1077): dashboard + headless Claude Code agent + editing engine, one Linux container.
# Build on the PC that has the code and models:  docker compose build
FROM node:22-bookworm-slim AS node
FROM python:3.12-slim-trixie

# Claude Code requires Node >=22. Use the official runtime rather than Debian's Node 20.
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

ENV PYTHONUNBUFFERED=1 PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PIP_NO_CACHE_DIR=1 DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 LC_ALL=C.UTF-8

# ffmpeg (7.x on trixie), Node for Claude Code, tini as PID 1 (reaps the agent's child processes), fonts for drawtext
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg libstdc++6 tini curl ca-certificates git procps fonts-dejavu-core fontconfig librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*

# Claude Code CLI, same version as on the PC (2026-11-12)
ARG CLAUDE_CODE_VERSION=2.1.322
RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} && npm cache clean --force

# Engine + ASR dependencies (versions from the PC's working venvs)
COPY deploy/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Non-root user; its home holds the Claude login + MCP config (a volume), /data holds jobs (a volume)
RUN useradd -m -u 1000 -s /bin/bash app \
    && mkdir -p /data /home/app/.claude \
    && chown -R app:app /data /home/app

WORKDIR /app
COPY --chown=app:app . /app
RUN chmod +x /app/deploy/entrypoint.sh

ENV HOME=/home/app \
    DASH_HOST=0.0.0.0 DASH_PORT=8050 \
    DASH_DATA=/data DASH_STYLES=/data/styles DASH_STYLE_NOTES=/data/style_notes_custom.json \
    DASH_AUTH=1 \
    DASH_CLAUDE_AUTH=api \
    DASH_RETENTION_DAYS=14 \
    HF_HOME=/data/cache/hf

USER app
EXPOSE 8050
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fs http://127.0.0.1:8050/api/me >/dev/null || exit 1
ENTRYPOINT ["/usr/bin/tini", "--", "/app/deploy/entrypoint.sh"]
