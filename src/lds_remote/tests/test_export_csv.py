"""Tests for the 361-column database export."""

import json
import unittest

from lds_remote.export_csv import rows_to_dataframe


class ExportTests(unittest.TestCase):
    """Check that SQL rows become a fixed table."""

    def test_json_row_becomes_360_ranges_plus_action(self):
        frame = rows_to_dataframe([(json.dumps([1.25] * 360), "go_forward")])
        self.assertEqual(frame.shape, (1, 361))
        self.assertEqual(frame.iloc[0]["range_000"], 1.25)
        self.assertEqual(frame.iloc[0]["range_359"], 1.25)
        self.assertEqual(frame.iloc[0]["action"], "go_forward")

    def test_incomplete_row_is_rejected(self):
        with self.assertRaises(ValueError):
            rows_to_dataframe([(json.dumps([1.0] * 359), "stop")])


if __name__ == "__main__":
    unittest.main()
