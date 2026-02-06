import os
import re
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
        "DATABASE=master;"
        f"UID={user};"
        f"PWD={password};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust_server_cert};"
        "Connection Timeout=5;"
    )

    max_wait_seconds = int(os.getenv("DB_INIT_MAX_WAIT", "90"))
    start = time.time()
    last_error: Exception | None = None

    # NOTE: Parameter markers (`?`) are surprisingly constrained in some T-SQL
    # contexts via ODBC (e.g. `DB_ID(N?)`, some `DECLARE` initializers).
    # To keep startup reliable, we validate the DB name and inline it.
    if not re.fullmatch(r"[A-Za-z0-9_-]+", database):
        raise RuntimeError(
            "DB_NAME contains unsupported characters; allowed: A-Z a-z 0-9 _ -"
        )

    db_id_literal = database.replace("'", "''")
    db_bracket_escaped = database.replace("]", "]]" )
    create_db_sql = (
        "IF DB_ID(N'" + db_id_literal + "') IS NULL "
        "BEGIN "
        "  EXEC(N'CREATE DATABASE [" + db_bracket_escaped + "]'); "
        "END"
    )

    while time.time() - start < max_wait_seconds:
        try:
            with pyodbc.connect(conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(create_db_sql)
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