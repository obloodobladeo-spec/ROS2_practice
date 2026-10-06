"""Tests for yellow line segmentation and steering."""

import cv2
import numpy as np

from opencv_pkg.vision import find_yellow_line, steering_for_line


def test_yellow_line_is_detected_in_lower_image():
    """The lower yellow stripe should supply a usable line position."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame, (100, 300), (130, 440), (0, 255, 255), -1)
    near_x, far_x, _, area = find_yellow_line(frame)
    assert 110 <= near_x <= 120
    assert far_x is not None
    assert area > 500


def test_upper_yellow_object_is_ignored():
    """A traffic signal above the road cannot steer the robot."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame, (100, 30), (200, 100), (0, 255, 255), -1)
    near_x, far_x, _, _ = find_yellow_line(frame)
    assert near_x is None
    assert far_x is None


def test_line_at_bottom_edge_is_detected():
    """A nearby line may occupy only the bottom edge of the camera image."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame, (0, 450), (340, 479), (0, 255, 255), -1)
    near_x, _, _, area = find_yellow_line(frame)
    assert 160 <= near_x <= 180
    assert area > 500


def test_lost_line_stops_and_left_line_steers_left():
    """Stop on line loss and turn toward a left-hand yellow marking."""
    assert steering_for_line(None, None, 640) == (0.0, 0.0)
    forward, turn = steering_for_line(100, 150, 640)
    assert forward > 0
    assert turn > 0


def test_far_curve_turns_before_near_line_moves():
    """A left curve in the lookahead region produces a left command."""
    _, turn = steering_for_line(160, 20, 640)
    assert turn > 0.2
