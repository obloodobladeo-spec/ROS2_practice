"""Publish randomized, geometrically consistent LDS-style laser scans."""

import math
import random

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class MockScanPublisher(Node):
    """Publish a 360-beam scan of randomized rectangular room walls."""

    def __init__(self):
        super().__init__('mock_scan_publisher')
        self.declare_parameter('topic', '/scan')
        self.declare_parameter('frame_id', 'laser')
        self.declare_parameter('publish_period', 2.0)
        self.declare_parameter('beam_count', 360)
        self.declare_parameter('range_min', 0.12)
        self.declare_parameter('range_max', 8.0)

        self._topic = str(self.get_parameter('topic').value)
        self._frame_id = str(self.get_parameter('frame_id').value)
        self._period = float(self.get_parameter('publish_period').value)
        self._beam_count = int(self.get_parameter('beam_count').value)
        self._range_min = float(self.get_parameter('range_min').value)
        self._range_max = float(self.get_parameter('range_max').value)

        if self._period <= 0.0:
            raise ValueError('publish_period must be greater than zero')
        if self._beam_count < 4:
            raise ValueError('beam_count must be at least 4')
        if not 0.0 < self._range_min < self._range_max:
            raise ValueError('range limits must satisfy 0 < range_min < range_max')

        self._publisher = self.create_publisher(LaserScan, self._topic, 10)
        self._timer = self.create_timer(self._period, self._publish_scan)
        self.get_logger().info(
            f'Publishing {self._beam_count}-beam mock scans on {self._topic} '
            f'every {self._period:.1f} seconds')

    def _publish_scan(self):
        """Publish ranges to the four walls of a randomized rectangular room."""
        # Distances from the sensor origin to forward, rear, left, and right walls.
        # The forward wall sometimes gets close to provide an obstacle to avoid.
        front = random.uniform(0.45, 3.5)
        rear = random.uniform(1.0, 3.5)
        left = random.uniform(0.65, 3.5)
        right = random.uniform(0.65, 3.5)

        scan = LaserScan()
        scan.header.stamp = self.get_clock().now().to_msg()
        scan.header.frame_id = self._frame_id
        scan.angle_min = -math.pi
        scan.angle_increment = (2.0 * math.pi) / self._beam_count
        scan.angle_max = scan.angle_min + (
            (self._beam_count - 1) * scan.angle_increment)
        scan.time_increment = 0.0
        scan.scan_time = self._period
        scan.range_min = self._range_min
        scan.range_max = self._range_max

        ranges = []
        for index in range(self._beam_count):
            angle = scan.angle_min + index * scan.angle_increment
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)

            x_distance = (front / cos_angle if cos_angle > 1e-9
                          else rear / -cos_angle if cos_angle < -1e-9
                          else math.inf)
            y_distance = (left / sin_angle if sin_angle > 1e-9
                          else right / -sin_angle if sin_angle < -1e-9
                          else math.inf)
            measured = min(x_distance, y_distance)

            # Small measurement noise gives each scan a sensor-like variation.
            measured += random.gauss(0.0, 0.008)
            measured = min(max(measured, self._range_min), self._range_max)
            ranges.append(float(measured))

        scan.ranges = ranges
        scan.intensities = []
        self._publisher.publish(scan)


def main(args=None):
    """Run the mock scan publisher node."""
    rclpy.init(args=args)
    node = MockScanPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
