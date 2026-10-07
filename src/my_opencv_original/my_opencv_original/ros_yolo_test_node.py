# CVbridge 미사용
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import numpy as np
import cv2

def red_line(frame, data):
    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )


    # =========================
    # 빨간색 범위
    # 빨강은 HSV 양 끝에 걸쳐 있어서
    # 범위를 2개 사용
    # =========================

    # 빨강 범위 1
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])

    # 빨강 범위 2
    lower_red2 = np.array([170, 70, 70])
    upper_red2 = np.array([179, 255, 255])


    # =========================
    # 빨간색 마스크 생성
    # =========================
    mask1 = cv2.inRange(
        hsv,
        lower_red1,
        upper_red1
    )

    mask2 = cv2.inRange(
        hsv,
        lower_red2,
        upper_red2
    )

    mask = cv2.bitwise_or(
        mask1,
        mask2
    )


    # =========================
    # 노이즈 제거
    # =========================
    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )


    # =========================
    # 빨간색 윤곽선 찾기
    # =========================
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )


    # 기본값: 빨간색 못 찾으면 정지
    data.linear.x = 0.
    data.angular.z = 0.
    detected = False


    # =========================
    # 빨간색이 발견된 경우
    # =========================
    if contours:

        # 가장 큰 빨간색 영역
        largest = max(
            contours,
            key=cv2.contourArea
        )

        area = cv2.contourArea(largest)


        # 너무 작은 빨간 점은 무시
        if area > 100:

            M = cv2.moments(largest)

            if M["m00"] != 0:

                detected = True

                # 빨간색 중심 좌표
                cx = int(
                    M["m10"] /
                    M["m00"]
                )

                cy = int(
                    M["m01"] /
                    M["m00"]
                )


                # =========================
                # 화면 크기
                # =========================
                height, width = frame.shape[:2]


                # =========================
                # 방향 판단
                #
                # 왼쪽 40%
                # 중앙 20%
                # 오른쪽 40%
                # =========================

                if cx < width * 0.4:

                    data.angular.z = 0.2

                elif cx > width * 0.6:

                    data.angular.z = -0.2

                else:

                    data.linear.x = 0.2


                # =========================
                # 화면에 검출 표시
                # =========================
                cv2.drawContours(
                    frame,
                    [largest],
                    -1,
                    (255, 0, 0),
                    2
                )

                cv2.circle(
                    frame,
                    (cx, cy),
                    15,
                    (0, 255, 255),
                    3
                )

                cv2.putText(
                    frame,
                    f"RED ({cx}, {cy})",
                    (cx + 10, cy),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    2
                )


    # =========================
    # 화면 중앙 영역 표시
    # =========================
    height, width = frame.shape[:2]

    left_line = int(width * 0.4)
    right_line = int(width * 0.6)


    cv2.line(
        frame,
        (left_line, 0),
        (left_line, height),
        (255, 255, 255),
        1
    )

    cv2.line(
        frame,
        (right_line, 0),
        (right_line, height),
        (255, 255, 255),
        1
    )

    return data

class ImageSubscriberNoBridge(Node):

    def __init__(self):
        super().__init__('image_sub_no_bridge')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self._publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        self.data = Twist()

    def image_callback(self, msg):
        img_arr = np.frombuffer(msg.data, dtype=np.uint8)
        cv_image = img_arr.reshape((msg.height, msg.width, -1))

        if msg.encoding == 'rgb8':
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)

        self.data = red_line(cv_image, self.data)

        self._publisher_.publish(self.data)

        cv2.imshow("Camera Topic", cv_image)
        cv2.waitKey(1) # 주기는 FPS 따라서 적절하게!

def main():
    rclpy.init()
    node = ImageSubscriberNoBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
