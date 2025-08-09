#!/usr/bin/env bash
set -euo pipefail

# Always run from repo root
cd "$(dirname "$0")"

# Load environment variables from .env if present
if [ -f ./.env ]; then
  set -a
  . ./.env
  set +a
fi

# Activate virtual environment
if [ -f ./venv/bin/activate ]; then
  source ./venv/bin/activate
else
  echo "Virtualenv not found at ./venv. Create it and install deps before continuing." >&2
  exit 1
fi

# Run Django management command
python manage.py "$@" 