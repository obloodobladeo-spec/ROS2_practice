"""MySQL storage for normalized scans and driving decisions."""

import json
import os
from datetime import datetime, timezone

import pymysql


def connect_database():
    """Connect using environment variables, without storing secrets in code."""
    user = os.environ.get("LDS_DB_USER")
    password = os.environ.get("LDS_DB_PASSWORD")
    if not user or password is None:
        raise ValueError("set LDS_DB_USER and LDS_DB_PASSWORD")
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
