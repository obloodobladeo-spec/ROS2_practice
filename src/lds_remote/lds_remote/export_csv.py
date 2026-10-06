"""Export stored scans as 360 distance columns plus one action column."""

import argparse
import json

import pandas as pd

from lds_remote.database import connect_database

RANGE_COLUMNS = [f"range_{degree:03d}" for degree in range(360)]


def rows_to_dataframe(rows):
    """Parse MySQL JSON values into a 361-column DataFrame."""
    records = []
    for ranges_json, action in rows:
        ranges = json.loads(ranges_json) if isinstance(ranges_json, str) else ranges_json
        if not isinstance(ranges, list) or len(ranges) != 360:
            raise ValueError("database row does not contain exactly 360 ranges")
        records.append(dict(zip(RANGE_COLUMNS, ranges), action=action))
    return pd.DataFrame.from_records(records, columns=RANGE_COLUMNS + ["action"])


def main():
    """Read MySQL and write one CSV suitable for later analysis."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="lidardata.csv")
    args = parser.parse_args()

    connection = connect_database()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT ranges, action FROM lidardata")
            frame = rows_to_dataframe(cursor.fetchall())
    finally:
        connection.close()
    frame.to_csv(args.output, index=False)
    print(f"Wrote {len(frame)} rows and {len(frame.columns)} columns to {args.output}")


if __name__ == "__main__":
    main()
