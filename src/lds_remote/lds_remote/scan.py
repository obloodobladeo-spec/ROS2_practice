"""Convert LaserScan messages into a fixed 360-degree driving view."""

import math
from statistics import median

POINT_COUNT = 360
ACTIONS = ("go_forward", "turn_left", "turn_right", "stop")


def normalize_scan(scan):
    """Return one finite distance per degree, with zero degrees facing forward."""
    raw_ranges = scan["ranges"]
    angle_min = float(scan["angle_min"])
    angle_increment = float(scan["angle_increment"])
    range_min = float(scan["range_min"])
    range_max = float(scan["range_max"])

    if not raw_ranges or not math.isfinite(angle_min):
        raise ValueError("scan has no ranges or a non-finite starting angle")
    if not math.isfinite(angle_increment) or angle_increment == 0:
        raise ValueError("scan has an invalid angle_increment")
    if len(raw_ranges) * abs(angle_increment) < math.radians(340):
        raise ValueError("scan does not cover enough of the full circle")
    if not 0 <= range_min < range_max or not math.isfinite(range_max):
        raise ValueError("scan has invalid range limits")

    result = [range_max] * POINT_COUNT
    observed = [False] * POINT_COUNT
    for index, raw_distance in enumerate(raw_ranges):
        # JSON has no infinity value. rosbridge sends Gazebo's +inf
        # (no return within range_max) as null.
        distance = range_max if raw_distance is None else float(raw_distance)
        if math.isnan(distance) or distance < range_min:
            continue
        if math.isinf(distance):
            if distance < 0:
                continue
            distance = range_max
        distance = min(distance, range_max)
        degree = round(math.degrees(angle_min + index * angle_increment)) % POINT_COUNT
        result[degree] = min(result[degree], distance)
        observed[degree] = True

    sectors = (
        list(range(350, 360)) + list(range(10)),
        list(range(80, 100)),
        list(range(260, 280)),
    )
    if any(sum(observed[degree] for degree in sector) < 10 for sector in sectors):
        raise ValueError("scan is missing forward or side distances")
    return result


def sector_distance(ranges, degrees):
    """Use a median so a single bad return does not trigger a turn."""
    return median(ranges[degree % POINT_COUNT] for degree in degrees)


def choose_action(ranges, safe_distance=0.75):
    """Choose a simple collision-avoidance action from 360 distances."""
    if len(ranges) != POINT_COUNT:
        raise ValueError("a driving view must have exactly 360 distances")
    if safe_distance <= 0:
        raise ValueError("safe_distance must be positive")

    # A median over the whole front arc can hide a narrow obstacle. Check
    # three smaller arcs, including the front corners of the wider Waffle Pi.
    front = min(
        sector_distance(ranges, range(330, 350)),
        sector_distance(ranges, list(range(350, 360)) + list(range(10))),
        sector_distance(ranges, range(10, 30)),
    )
    left = min(
        sector_distance(ranges, range(30, 70)),
        sector_distance(ranges, range(70, 110)),
    )
    right = min(
        sector_distance(ranges, range(290, 330)),
        sector_distance(ranges, range(250, 290)),
    )
    if front >= safe_distance:
        return "go_forward"
    # A corridor can be narrower than the forward stopping distance while
    # still leaving room to rotate in place.
    turn_clearance = max(0.32, safe_distance * 0.5)
    if left < turn_clearance and right < turn_clearance:
        return "stop"
    if left < turn_clearance:
        return "turn_right"
    if right < turn_clearance:
        return "turn_left"
    return "turn_left" if left >= right else "turn_right"


def twist_for_action(action, linear_speed=0.12, angular_speed=0.7):
    """Build the roslibpy representation of geometry_msgs/Twist."""
    if action not in ACTIONS:
        raise ValueError(f"unknown action: {action}")
    if linear_speed < 0 or angular_speed < 0:
        raise ValueError("speeds must be non-negative")
    linear_x = linear_speed if action == "go_forward" else 0.0
    angular_z = 0.0
    if action == "turn_left":
        angular_z = angular_speed
    elif action == "turn_right":
        angular_z = -angular_speed
    return {
        "linear": {"x": linear_x, "y": 0.0, "z": 0.0},
        "angular": {"x": 0.0, "y": 0.0, "z": angular_z},
    }
