#!/bin/bash
set -e
echo "=== MindWell Counselling — Vercel Build ==="

# Install dependencies
pip3 install --break-system-packages -r counseling_app/requirements.txt

# Set Python path so Django can find counseling_app.settings
export PYTHONPATH="${PYTHONPATH}:$(pwd)/counseling_app"
export DJANGO_SETTINGS_MODULE="counseling_app.settings"

# collectstatic — skip if DATABASE_URL not set (Vercel build may not have it)
# WhiteNoise handles static serving at runtime; this just pre-compresses files.
echo "Running collectstatic..."
python3 counseling_app/manage.py collectstatic --noinput --clear

echo "=== Build complete ==="
