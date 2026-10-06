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

    def test_rosbridge_null_no_return_uses_range_max(self):
        scan = {
            "angle_min": 0.0,
            "angle_increment": math.pi / 180,
            "range_min": 0.12,
            "range_max": 3.5,
            "ranges": [None] * 360,
        }
        scan["ranges"][0] = 0.6
        normalized = normalize_scan(scan)
        self.assertEqual(normalized[0], 0.6)
        self.assertEqual(normalized[1], 3.5)

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

    def test_front_corner_obstacle_triggers_turn(self):
        ranges = [3.5] * 360
        for degree in range(15, 29):
            ranges[degree] = 0.45
        self.assertEqual(choose_action(ranges, safe_distance=0.75), "turn_left")
        self.assertEqual(twist_for_action("turn_left")["linear"]["x"], 0.0)

    def test_narrow_corridor_still_allows_in_place_turn(self):
        ranges = [3.5] * 360
        for degree in list(range(350, 360)) + list(range(10)):
            ranges[degree] = 0.5
        for degree in range(30, 110):
            ranges[degree] = 0.45
        for degree in range(250, 330):
            ranges[degree] = 0.55
        self.assertEqual(choose_action(ranges, safe_distance=0.75), "turn_right")

    def test_too_little_room_on_both_sides_stops(self):
        ranges = [0.25] * 360
        self.assertEqual(choose_action(ranges, safe_distance=0.75), "stop")

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
