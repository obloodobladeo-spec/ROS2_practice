"""cv_bridge를 이용해 ROS 카메라 영상을 OpenCV 창에 표시합니다."""

import cv2
import rclpy
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class CameraCvBridge(Node):
    """Image 메시지를 cv_bridge로 변환하는 기본 예제입니다."""

    def __init__(self):
        """카메라 토픽 구독자와 변환 도구를 준비합니다."""
        super().__init__('camera_cv_bridge')
        self.bridge = CvBridge()
        self.stop_requested = False
        self.create_subscription(
            Image, '/camera/image_raw', self.on_image, qos_profile_sensor_data)
        self.get_logger().info('/camera/image_raw 구독 중. 창에서 q를 누르면 종료합니다.')

    def on_image(self, message):
        """ROS Image 한 장을 받아 BGR 영상으로 변환합니다."""
        try:
            # ROS Image에는 픽셀 바이트와 너비, 높이, 색상 형식이 따로 있습니다.
            # cv_bridge가 이 정보를 읽어 OpenCV의 높이×너비×3 배열로 바꿉니다.
            # OpenCV 화면은 BGR 순서를 사용하므로 bgr8을 요청합니다.
            frame = self.bridge.imgmsg_to_cv2(
                message, desired_encoding='bgr8')
        except CvBridgeError as error:
            self.get_logger().warning(f'영상 변환 실패: {error}')
            return

        cv2.imshow('cv_bridge camera', frame)
        if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
            self.stop_requested = True


def main():
    """카메라 창을 열고 q, Esc 또는 Ctrl+C까지 영상을 표시합니다."""
    rclpy.init()
    node = CameraCvBridge()
    try:
        while rclpy.ok() and not node.stop_requested:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
