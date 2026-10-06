"""Tests for timestamps saved with scan decisions."""

import unittest
from datetime import datetime, timezone

from lds_remote.drive import parse_args, scan_timestamp


class TimestampTests(unittest.TestCase):
    """Keep Gazebo simulation time out of the MySQL datetime column."""

    def test_simulated_stamp_uses_current_utc_time(self):
        before = datetime.now(timezone.utc).replace(tzinfo=None)
        timestamp = scan_timestamp({"header": {"stamp": {"sec": 92, "nanosec": 0}}})
        after = datetime.now(timezone.utc).replace(tzinfo=None)
        self.assertLessEqual(before, timestamp)
        self.assertLessEqual(timestamp, after)

    def test_wall_clock_stamp_is_preserved(self):
        timestamp = scan_timestamp({
            "header": {"stamp": {"sec": 1791265532, "nanosec": 500000000}},
        })
        expected = datetime(2026, 10, 6, 5, 45, 32, 500000, tzinfo=timezone.utc)
        self.assertEqual(timestamp, expected.replace(tzinfo=None))


class ArgumentTests(unittest.TestCase):
    """Check the database-free driving option."""

    def test_no_db_flag(self):
        args = parse_args(["--no-db", "--scan-topic", "/mock_scan"])
        self.assertTrue(args.no_db)
        self.assertEqual(args.scan_topic, "/mock_scan")


if __name__ == "__main__":
    unittest.main()
