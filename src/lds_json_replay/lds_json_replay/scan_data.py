"""Read and validate one 360-point LDS JSON scan."""

import json
import math
from pathlib import Path


def load_scan_file(path):
    """Return validated scan fields from a JSON file."""
    with Path(path).open(encoding='utf-8') as stream:
        data = json.load(stream)

    angle_min = float(data['angle_min'])
    angle_max = float(data['angle_max'])
    angle_increment = float(data['angle_increment'])
    range_min = float(data['range_min'])
    range_max = float(data['range_max'])
    ranges = [float(value) for value in data['ranges']]
    intensities = [float(value) for value in data.get('intensities', [])]

    if len(ranges) != 360:
        raise ValueError(f'{path}: expected 360 ranges, got {len(ranges)}')
    if len(intensities) not in (0, 360):
        raise ValueError(f'{path}: intensities must be empty or have 360 values')
    fields = (angle_min, angle_max, angle_increment, range_min, range_max)
    if not all(math.isfinite(value) for value in fields):
        raise ValueError(f'{path}: scan geometry contains non-finite values')
    if angle_increment <= 0 or range_min < 0 or range_max <= range_min:
        raise ValueError(f'{path}: invalid scan geometry or range limits')
    if abs(angle_max - (angle_min + 359 * angle_increment)) > 0.001:
        raise ValueError(f'{path}: angle_max does not match 360 samples')
    if any(not math.isfinite(value) or value < range_min or value > range_max
           for value in ranges):
        raise ValueError(f'{path}: ranges contain out-of-range values')
    if any(not math.isfinite(value) for value in intensities):
        raise ValueError(f'{path}: intensities contain non-finite values')

    return {
        'angle_min': angle_min,
        'angle_max': angle_max,
        'angle_increment': angle_increment,
        'range_min': range_min,
        'range_max': range_max,
        'ranges': ranges,
        'intensities': intensities,
        'pattern': data.get('meta', {}).get('pattern', 'unknown'),
    }
