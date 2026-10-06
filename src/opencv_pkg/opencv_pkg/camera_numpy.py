"""cv_bridge 없이 ROS Image의 바이트를 NumPy 배열로 변환합니다."""

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


def image_to_bgr(message):
    """rgb8 또는 bgr8 Image 메시지를 OpenCV용 BGR 배열로 바꿉니다."""
    if message.encoding not in ('rgb8', 'bgr8'):
        raise ValueError(f'지원하지 않는 색상 형식: {message.encoding}')

    # rgb8/bgr8에서는 픽셀 하나가 R,G,B 또는 B,G,R 3바이트입니다.
    bytes_per_row = message.width * 3
    if message.step < bytes_per_row:
        raise ValueError('한 줄의 바이트 수(step)가 영상 너비보다 작습니다')

    # data는 1차원 바이트 배열입니다. NumPy가 같은 바이트를 숫자로 읽습니다.
    raw = np.frombuffer(message.data, dtype=np.uint8)
    if raw.size != message.height * message.step:
        raise ValueError('data 크기와 height × step이 일치하지 않습니다')

    # step은 한 줄의 전체 바이트 수입니다. 줄 끝 여백이 있을 수 있습니다.
    rows = raw.reshape(message.height, message.step)
    pixels = rows[:, :bytes_per_row]

    # 줄 끝 여백을 제외하고 (높이, 너비, 색상 3개) 배열로 만듭니다.
    frame = pixels.reshape(message.height, message.width, 3)

    # ROS 영상이 RGB라면 OpenCV 화면용 BGR 순서로 뒤집습니다.
    if message.encoding == 'rgb8':
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame.copy()


class CameraNumpy(Node):
    """Image.data를 직접 변환해 카메라 창에 표시하는 기본 예제입니다."""

    def __init__(self):
        """카메라 토픽 구독자를 준비합니다."""
        super().__init__('camera_numpy')
        self.stop_requested = False
        self.create_subscription(
            Image, '/camera/image_raw', self.on_image, qos_profile_sensor_data)
        self.get_logger().info('/camera/image_raw 구독 중. 창에서 q를 누르면 종료합니다.')

    def on_image(self, message):
        """카메라 메시지 한 장을 직접 변환해 표시합니다."""
        try:
            frame = image_to_bgr(message)
        except ValueError as error:
            self.get_logger().warning(str(error))
            return

        cv2.imshow('NumPy camera', frame)
        if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
            self.stop_requested = True


def main():
    """카메라 창을 열고 q, Esc 또는 Ctrl+C까지 영상을 표시합니다."""
    rclpy.init()
    node = CameraNumpy()
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
