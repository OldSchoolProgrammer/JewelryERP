#!/bin/sh
set -eu

APP_USER="${APP_USER:-appuser}"

echo "[entrypoint] Starting michaellobmapp"

run_as_appuser() {
  # Run a command as the app user when entrypoint is root.
  if [ "$(id -u)" = "0" ]; then
    gosu "$APP_USER" "$@"
  else
    "$@"
  fi
}

if [ "$(id -u)" = "0" ]; then
  echo "[entrypoint] Ensuring media/static directories are writable"
  mkdir -p /app/media/jewelry_images /app/media/certificates /app/staticfiles
  chown -R "$APP_USER":"$APP_USER" /app/media /app/staticfiles || true
  chmod -R u+rwX,g+rwX /app/media /app/staticfiles || true
fi

# Optional: create MSSQL database if needed
if [ "${DB_ENGINE:-sqlite}" = "mssql" ]; then
  echo "[entrypoint] Initializing MSSQL database (if missing)"
  run_as_appuser python /app/scripts/init_mssql_db.py
fi

echo "[entrypoint] Running migrations"
run_as_appuser python manage.py migrate --noinput

echo "[entrypoint] Collecting static files"
run_as_appuser python manage.py collectstatic --noinput

echo "[entrypoint] Launching: $*"
if [ "$(id -u)" = "0" ]; then
  exec gosu "$APP_USER" "$@"
fi
exec "$@"
