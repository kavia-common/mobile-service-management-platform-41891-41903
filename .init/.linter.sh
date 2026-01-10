#!/bin/bash
set -euo pipefail

cd /home/kavia/workspace/code-generation/mobile-service-management-platform-41891-41903/mobile_service_backend

# CI hardening: create the venv if it doesn't exist (some pipelines run lint before buildCommand).
if [ ! -f "venv/bin/activate" ]; then
  python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

# Ensure dependencies (including flake8) are present.
pip install --no-cache-dir -r requirements.txt >/dev/null

flake8 .

