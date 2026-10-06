"""MySQL storage for normalized scans and driving decisions."""

import json
import os
import sys
from datetime import datetime, timezone
from getpass import getpass

import pymysql


def connect_database():
    """Connect using environment variables or an interactive password prompt."""
    user = os.environ.get("LDS_DB_USER", "rosuser")
    password = os.environ.get("LDS_DB_PASSWORD")
    if not user:
        raise ValueError("LDS_DB_USER cannot be empty")
    if password is None:
        if not sys.stdin.isatty():
            raise ValueError("set LDS_DB_PASSWORD for non-interactive use")
        password = getpass("MySQL password: ")
    return pymysql.connect(
        host=os.environ.get("LDS_DB_HOST", "localhost"),
        port=int(os.environ.get("LDS_DB_PORT", "3306")),
        user=user,
        password=password,
        database=os.environ.get("LDS_DB_NAME", "lds_practice"),
        charset="utf8mb4",
        autocommit=True,
        connect_timeout=5,
    )


def save_scan(connection, ranges, action, measured_at=None):
    """Insert one 360-value scan and action with a UTC timestamp."""
    if len(ranges) != 360:
        raise ValueError("exactly 360 distances are required")
    if measured_at is None:
        measured_at = datetime.now(timezone.utc).replace(tzinfo=None)
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO lidardata (`ranges`, `when`, `action`) "
            "VALUES (%s, %s, %s)",
            (json.dumps(ranges, allow_nan=False), measured_at, action),
        )
