import os
import sys
import time

import pyodbc


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    host = _get_env("DB_HOST", "sqlserver")
    port = os.getenv("DB_PORT", "1433")
    user = _get_env("DB_USER", "sa")
    password = _get_env("DB_PASSWORD")
    database = _get_env("DB_NAME", "michaellobmdb")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")

    encrypt = os.getenv("DB_ENCRYPT", "yes")
    trust_server_cert = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

    server = f"{host},{port}"

    # Connect to master to create the application database if needed
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE=master;"
        f"UID={user};"
        f"PWD={password};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust_server_cert};"
        "Connection Timeout=5;"
    )

    max_wait_seconds = int(os.getenv("DB_INIT_MAX_WAIT", "90"))
    start = time.time()
    last_error: Exception | None = None

    while time.time() - start < max_wait_seconds:
        try:
            with pyodbc.connect(conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "IF DB_ID(N?) IS NULL BEGIN EXEC('CREATE DATABASE [' + REPLACE(?, ']', ']]') + ']') END",
                    database,
                    database,
                )
                return 0
        except Exception as exc:  # pragma: no cover
            last_error = exc
            time.sleep(2)

    raise RuntimeError(f"SQL Server not ready after {max_wait_seconds}s: {last_error}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"[init_mssql_db] ERROR: {e}", file=sys.stderr)
        raise
