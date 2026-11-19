#!/bin/sh
# Container start: prepare /data, refresh the built-in style plugins, start the dashboard.
set -e
mkdir -p /data/jobs /data/styles /data/cache "$HOME/.claude"

# The styles plugin lives on the data volume, because "Uslub yaratish" adds new skills to it at run time.
# Built-in skills are refreshed from the image on every start; skills created by the dashboard are kept.
cp -a /app/styles/. /data/styles/

python -I /app/deploy/setup_connections.py

exec python -I -u /app/dashboard/server.py --no-browser
