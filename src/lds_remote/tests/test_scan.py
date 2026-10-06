"""Tests for scan geometry and movement decisions."""

import math
import unittest

from lds_remote.scan import choose_action, normalize_scan, twist_for_action


class ScanTests(unittest.TestCase):
    """Check geometry independent of the sensor's starting angle."""

    def test_negative_pi_scan_maps_forward_to_degree_zero(self):
        scan = {
            "angle_min": -math.pi,
            "angle_increment": math.pi / 180,
            "range_min": 0.12,
            "range_max": 3.5,
            "ranges": [3.5] * 360,
        }
        scan["ranges"][180] = 0.4
        normalized = normalize_scan(scan)
        self.assertEqual(len(normalized), 360)
        self.assertAlmostEqual(normalized[0], 0.4)

    def test_blocked_front_turns_to_open_side(self):
        ranges = [3.5] * 360
        for degree in list(range(350, 360)) + list(range(10)):
            ranges[degree] = 0.4
        for degree in range(260, 280):
            ranges[degree] = 0.6
        self.assertEqual(choose_action(ranges), "turn_left")
        self.assertGreater(twist_for_action("turn_left")["angular"]["z"], 0)

    def test_open_front_goes_forward(self):
        self.assertEqual(choose_action([3.5] * 360), "go_forward")
        self.assertGreater(twist_for_action("go_forward")["linear"]["x"], 0)

    def test_no_usable_scan_is_rejected(self):
        scan = {
            "angle_min": 0.0,
            "angle_increment": math.pi / 180,
            "range_min": 0.12,
            "range_max": 3.5,
            "ranges": [float("nan")] * 360,
        }
        with self.assertRaises(ValueError):
            normalize_scan(scan)

    def test_partial_scan_is_rejected(self):
        scan = {
            "angle_min": -math.pi / 2,
            "angle_increment": math.pi / 180,
            "range_min": 0.12,
            "range_max": 3.5,
            "ranges": [1.0] * 180,
        }
        with self.assertRaises(ValueError):
            normalize_scan(scan)


if __name__ == "__main__":
    unittest.main()
