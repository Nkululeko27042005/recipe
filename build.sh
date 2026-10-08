#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations / create database tables
python -c "from app import create_app; from app.extensions import db; app = create_app(); ctx = app.app_context(); ctx.push(); db.create_all()"
