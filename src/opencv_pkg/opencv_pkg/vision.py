"""Detect the Autorace yellow lane marking and compute steering."""

import cv2
import numpy as np


def _largest_yellow_centroid(mask, top, bottom, min_area):
    """Find the largest yellow contour within one horizontal image band."""
    band = mask[top:bottom]
    contours, _ = cv2.findContours(band, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, 0.0
    contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(contour)
    if area < min_area:
        return None, area
    moments = cv2.moments(contour)
    if moments['m00'] == 0:
        return None, area
    return moments['m10'] / moments['m00'], area


def find_yellow_line(frame, min_area=500):
    """Return near/far line positions, yellow mask, and detected area."""
    height, _ = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (18, 80, 80), (38, 255, 255))
    mask[:int(height * 0.56)] = 0
    kernel = np.ones((3, 3), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    split = int(height * 0.75)
    near_x, near_area = _largest_yellow_centroid(
        mask, split, height, min_area)
    far_x, far_area = _largest_yellow_centroid(
        mask, int(height * 0.56), split, min_area * 0.5)
    return near_x, far_x, mask, near_area + far_area


def steering_for_line(near_x, far_x, width, speed=0.06, gain=1.8,
                      max_turn=0.8, target_fraction=0.25):
    """Use a near offset and a lookahead offset to follow the left line."""
    if near_x is None and far_x is None:
        return 0.0, 0.0
    errors = []
    weights = []
    if near_x is not None:
        errors.append((width * target_fraction - near_x) / (width / 2))
        weights.append(0.55)
    if far_x is not None:
        far_target = min(0.9, target_fraction + 0.07)
        errors.append((width * far_target - far_x) / (width / 2))
        weights.append(0.45)
    error = sum(weight * value for weight, value in zip(weights, errors))
    error /= sum(weights)
    turn = max(-max_turn, min(max_turn, gain * error))
    forward = speed * (1.0 - 0.6 * abs(turn) / max_turn)
    if near_x is None:
        forward *= 0.4
    return forward, turn
