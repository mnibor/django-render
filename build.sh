#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
# Seed idempotente (no duplica si ya existe)
python manage.py seed_data || true
