"""Show the Waffle Pi camera and steer along the Autorace yellow line."""

import argparse
import time

import cv2
import rclpy
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import Image

from opencv_pkg.vision import find_yellow_line, steering_for_line


class YellowLineFollower(Node):
    """Subscribe to Gazebo camera images and publish safe velocity commands."""

    def __init__(self, args):
        super().__init__('yellow_line_follower')
        self.args = args
        self.bridge = CvBridge()
        self.latest_frame = None
        self.last_image_time = None
        self.last_line_time = None
        self.near_x = None
        self.far_x = None
        self.mask = None
        self.area = 0.0
        self.publisher = self.create_publisher(Twist, args.cmd_topic, 10)
        self.subscription = self.create_subscription(
            Image, args.image_topic, self.on_image, qos_profile_sensor_data)
        self.timer = self.create_timer(0.1, self.control_step)
        self.get_logger().info(
            f'Watching {args.image_topic}; publishing {args.cmd_topic}. '
            'Press q or Esc in the camera window to stop.')

    def on_image(self, message):
        """Convert and analyze the newest camera image."""
        try:
            frame = self.bridge.imgmsg_to_cv2(message, desired_encoding='bgr8')
        except CvBridgeError as error:
            self.get_logger().warning(f'Image conversion failed: {error}')
            return
        self.latest_frame = frame
        self.last_image_time = time.monotonic()
        self.near_x, self.far_x, self.mask, self.area = find_yellow_line(
            frame, self.args.min_area)
        if self.near_x is not None or self.far_x is not None:
            self.last_line_time = self.last_image_time

    def publish_velocity(self, forward, turn):
        """Publish a planar Twist command."""
        command = Twist()
        command.linear.x = float(forward)
        command.angular.z = float(turn)
        self.publisher.publish(command)

    def control_step(self):
        """Stop on missing images or a lost line; otherwise follow the line."""
        now = time.monotonic()
        image_is_fresh = (
            self.last_image_time is not None and
            now - self.last_image_time <= self.args.stale_timeout)
        line_is_fresh = (
            self.last_line_time is not None and
            now - self.last_line_time <= self.args.line_timeout)
        if (not image_is_fresh or not line_is_fresh or
                (self.near_x is None and self.far_x is None)):
            self.publish_velocity(0.0, 0.0)
            return
        forward, turn = steering_for_line(
            self.near_x, self.far_x, self.latest_frame.shape[1],
            speed=self.args.speed, gain=self.args.gain,
            max_turn=self.args.max_turn,
            target_fraction=self.args.target_fraction)
        self.publish_velocity(forward, turn)

    def show_camera(self):
        """Render the camera frame and yellow mask in one OpenCV window."""
        if self.latest_frame is None:
            return False
        frame = self.latest_frame.copy()
        height, width = frame.shape[:2]
        target_x = int(width * self.args.target_fraction)
        cv2.line(frame, (target_x, int(height * 0.56)),
                 (target_x, height - 1), (255, 0, 0), 2)
        line_found = self.near_x is not None or self.far_x is not None
        image_is_fresh = (
            self.last_image_time is not None and
            time.monotonic() - self.last_image_time <= self.args.stale_timeout)
        if line_found:
            if self.near_x is not None:
                cv2.line(frame, (int(self.near_x), int(height * 0.75)),
                         (int(self.near_x), height - 1), (0, 255, 0), 2)
            if self.far_x is not None:
                cv2.line(frame, (int(self.far_x), int(height * 0.56)),
                         (int(self.far_x), int(height * 0.75)),
                         (0, 200, 255), 2)
            label = f'yellow near/far area={self.area:.0f}'
        else:
            label = 'yellow line lost: STOP'
        if not image_is_fresh:
            label = 'camera stale: STOP'
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0) if line_found and image_is_fresh else
                    (0, 0, 255), 2)
        mask_color = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)
        display = cv2.hconcat([frame, mask_color])
        cv2.imshow('Waffle Pi yellow line | camera / mask', display)
        return cv2.waitKey(1) & 0xFF in (ord('q'), 27)

    def stop(self):
        """Send a final zero velocity command before shutting down."""
        self.publish_velocity(0.0, 0.0)


def parse_args(argv=None):
    """Parse camera topic, controller tuning, and display options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image-topic', default='/camera/image_raw')
    parser.add_argument('--cmd-topic', default='/cmd_vel')
    parser.add_argument('--speed', type=float, default=0.06)
    parser.add_argument('--gain', type=float, default=1.8)
    parser.add_argument('--max-turn', type=float, default=0.8)
    parser.add_argument('--target-fraction', type=float, default=0.25)
    parser.add_argument('--min-area', type=float, default=500.0)
    parser.add_argument('--stale-timeout', type=float, default=0.7)
    parser.add_argument('--line-timeout', type=float, default=0.7)
    parser.add_argument('--no-display', action='store_true')
    args = parser.parse_args(argv)
    if args.speed < 0 or args.gain < 0 or args.max_turn <= 0:
        parser.error('speed and gain must be non-negative; max-turn positive')
    if not 0 < args.target_fraction < 1 or args.min_area <= 0:
        parser.error('target-fraction must be in (0, 1); min-area positive')
    if args.stale_timeout <= 0 or args.line_timeout <= 0:
        parser.error('timeouts must be positive')
    return args


def main(argv=None):
    """Run until Ctrl+C or the camera window's q/Esc key is pressed."""
    args = parse_args(argv)
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    follower = YellowLineFollower(args)
    try:
        while rclpy.ok():
            rclpy.spin_once(follower, timeout_sec=0.03)
            if not args.no_display and follower.show_camera():
                break
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            follower.stop()
            time.sleep(0.1)
        follower.destroy_node()
        if not args.no_display:
            cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
