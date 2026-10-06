"""Publish LaserScan messages loaded from existing JSON files."""

import random
from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

from lds_json_replay.scan_data import load_scan_file


class JsonScanPublisher(Node):
    """Select a JSON file every period and publish its ranges as /scan."""

    def __init__(self):
        super().__init__('json_scan_publisher')
        self.declare_parameter('json_dir', '')
        self.declare_parameter('topic', '/scan')
        self.declare_parameter('frame_id', 'laser')
        self.declare_parameter('publish_period', 2.0)
        self.declare_parameter('selection_mode', 'random')

        json_dir = Path(self.get_parameter('json_dir').value).expanduser()
        topic = self.get_parameter('topic').value
        self.frame_id = self.get_parameter('frame_id').value
        self.period = float(self.get_parameter('publish_period').value)
        self.selection_mode = self.get_parameter('selection_mode').value
        if self.period <= 0:
            raise ValueError('publish_period must be positive')
        if self.selection_mode not in ('random', 'sequential'):
            raise ValueError('selection_mode must be random or sequential')
        if not json_dir.is_dir():
            raise ValueError(f'json_dir is not a directory: {json_dir}')

        self.files = sorted(json_dir.glob('*.json'))
        if not self.files:
            raise ValueError(f'no JSON files in {json_dir}')
        self.next_index = 0
        self.publisher = self.create_publisher(LaserScan, topic, 10)
        self.timer = self.create_timer(self.period, self.publish_scan)
        self.get_logger().info(
            f'Replaying {len(self.files)} JSON scans on {topic} '
            f'every {self.period} seconds')

    def publish_scan(self):
        """Convert one stored scan to a fresh timestamped ROS message."""
        if self.selection_mode == 'random':
            path = random.choice(self.files)
        else:
            path = self.files[self.next_index]
            self.next_index = (self.next_index + 1) % len(self.files)
        try:
            data = load_scan_file(path)
        except (OSError, KeyError, TypeError, ValueError) as exc:
            self.get_logger().error(f'Skipping {path.name}: {exc}')
            return

        message = LaserScan()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = self.frame_id
        message.angle_min = data['angle_min']
        message.angle_max = data['angle_max']
        message.angle_increment = data['angle_increment']
        message.range_min = data['range_min']
        message.range_max = data['range_max']
        message.scan_time = self.period
        message.time_increment = self.period / len(data['ranges'])
        message.ranges = data['ranges']
        message.intensities = data['intensities']
        self.publisher.publish(message)
        self.get_logger().info(
            f'Published {path.name} (pattern={data["pattern"]})')


def main(args=None):
    """Run the ROS node until interrupted."""
    rclpy.init(args=args)
    node = None
    try:
        node = JsonScanPublisher()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
