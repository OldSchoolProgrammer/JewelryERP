#!/bin/sh
set -eu

echo "[entrypoint] Starting michaellobmapp"

# Optional: create MSSQL database if needed
if [ "${DB_ENGINE:-sqlite}" = "mssql" ]; then
  echo "[entrypoint] Initializing MSSQL database (if missing)"
  python /app/scripts/init_mssql_db.py
fi

echo "[entrypoint] Running migrations"
python manage.py migrate --noinput

echo "[entrypoint] Collecting static files"
python manage.py collectstatic --noinput

echo "[entrypoint] Launching web server: $*"
exec "$@"
