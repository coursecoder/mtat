#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Install dependencies into the venv
.venv/bin/pip install --quiet -r requirements.txt

# Persist the venv activation for the session
echo 'export PATH="$CLAUDE_PROJECT_DIR/.venv/bin:$PATH"' >> "$CLAUDE_ENV_FILE"
echo 'export VIRTUAL_ENV="$CLAUDE_PROJECT_DIR/.venv"' >> "$CLAUDE_ENV_FILE"
