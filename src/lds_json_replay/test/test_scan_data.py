"""Tests for loading the exercise's JSON scan format."""

import json
import math
import tempfile
import unittest
from pathlib import Path

from lds_json_replay.scan_data import load_scan_file


class ScanDataTests(unittest.TestCase):
    """Check that malformed files cannot be published as LaserScan."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / 'scan.json'
        self.scan = {
            'angle_min': 0.0,
            'angle_max': math.radians(359),
            'angle_increment': math.radians(1),
            'range_min': 0.12,
            'range_max': 3.5,
            'ranges': [3.5] * 360,
            'intensities': [100.0] * 360,
            'meta': {'pattern': 'front_wall'},
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_scan(self):
        """Write the current test fixture as JSON."""
        self.path.write_text(json.dumps(self.scan), encoding='utf-8')

    def test_valid_scan(self):
        self.write_scan()
        result = load_scan_file(self.path)
        self.assertEqual(len(result['ranges']), 360)
        self.assertEqual(result['pattern'], 'front_wall')

    def test_short_scan_is_rejected(self):
        self.scan['ranges'].pop()
        self.write_scan()
        with self.assertRaises(ValueError):
            load_scan_file(self.path)

    def test_out_of_range_distance_is_rejected(self):
        self.scan['ranges'][0] = 4.0
        self.write_scan()
        with self.assertRaises(ValueError):
            load_scan_file(self.path)


if __name__ == '__main__':
    unittest.main()
