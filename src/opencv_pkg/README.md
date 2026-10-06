# Waffle Pi 노란선 추종

`opencv_pkg`는 Gazebo Waffle Pi의 `/camera/image_raw` 영상을 OpenCV로 분석해 Autorace 2020 코스의 노란선을 따라갑니다. [`opencv_follow.py`](opencv_pkg/opencv_follow.py)는 카메라 영상과 노란색 검출 마스크를 한 창에 표시하고 `/cmd_vel`에 속도 명령을 발행하는 독립 실행 노드입니다.

화면의 파란 선은 가까운 노란선이 오기를 바라는 위치, 초록 선은 검출한 가까운 노란선, 주황 선은 앞쪽 노란선입니다. 영상이 끊기거나 노란선을 찾지 못하면 정지합니다. 이 패키지는 MySQL을 사용하지 않습니다.

## 빌드

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select opencv_pkg --symlink-install
```

## 실행

기존 `lds_remote.drive` 등 `/cmd_vel`을 발행하는 프로그램은 먼저 종료합니다. 터미널 1에서 카메라가 있는 `waffle_pi` 모델과 Autorace 2020 월드를 실행합니다.

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_autorace_2020.launch.py
```

터미널 2에서 OpenCV 주행 노드를 실행합니다.

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run opencv_pkg opencv_follow
```

카메라 창에서 `q` 또는 `Esc`를 누르거나 터미널에서 `Ctrl+C`를 누르면 마지막으로 0 속도 명령을 보내고 종료합니다. 그래픽 창을 사용할 수 없는 환경에서 동작만 확인하려면 `--no-display`를 추가합니다.

```bash
ros2 run opencv_pkg opencv_follow --no-display
```

`--speed`, `--gain`, `--max-turn`, `--target-fraction`, `--min-area`, `--image-topic`, `--cmd-topic`으로 동작을 조정할 수 있습니다. 기본값은 설치된 Waffle Pi Autorace 월드의 카메라에 맞췄습니다.

## 카메라 영상 변환 기본 예제

Gazebo를 위의 `waffle_pi` 설정으로 실행한 뒤, 새 터미널에서 아래 두 명령 중 하나를 실행합니다. 두 예제 모두 `/camera/image_raw`를 구독해 화면에 표시하며, 주행 명령이나 데이터베이스 기록은 하지 않습니다.

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run opencv_pkg camera_cv_bridge
```

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run opencv_pkg camera_numpy
```

창에서 `q` 또는 `Esc`를 누르면 종료합니다. 각각 별도 창이 열리므로 처음에는 하나씩 실행해 보세요.

- [`camera_cv_bridge.py`](opencv_pkg/camera_cv_bridge.py): `CvBridge.imgmsg_to_cv2(message, desired_encoding='bgr8')` 한 줄로 ROS `Image`를 OpenCV 배열로 바꿉니다. 색상 순서도 라이브러리가 처리합니다.
- [`camera_numpy.py`](opencv_pkg/camera_numpy.py): `Image.data`의 1차원 바이트를 NumPy로 읽습니다. `height`와 `step`으로 줄을 나누고, 줄 끝 여백을 제외한 뒤 `(height, width, 3)` 모양으로 만듭니다. `rgb8` 영상이면 RGB를 OpenCV용 BGR로 바꿉니다. 이 기본 예제는 `rgb8`과 `bgr8`만 지원합니다.

ROS `Image`는 픽셀 값(`data`), 가로·세로 크기(`width`, `height`), 한 줄의 바이트 수(`step`), 색상 형식(`encoding`)을 따로 담습니다. 두 파일의 주석을 위에서 아래로 읽으면 같은 영상을 각각 어떻게 변환하는지 볼 수 있습니다.

## 실제로 겪은 문제

1. **문제:** `/camera/image_raw`가 목록에 있지만 영상이 안 나왔습니다. **원인:** `burger`에는 카메라 발행자가 없었고 rqt 구독 때문에 토픽 이름만 보였습니다. **해결:** `TURTLEBOT3_MODEL=waffle_pi`로 Gazebo를 다시 시작하고 `ros2 topic info /camera/image_raw`에서 발행자를 확인합니다.
2. **문제:** 곡선에서 노란선이 사라지며 정지했습니다. **원인:** 검출 영역이 화면 맨 아래를 제외했습니다. **해결:** 하단까지 검사하고 가까운 선과 앞쪽 선을 함께 사용합니다.
3. **문제:** `Ctrl+C` 종료 시 정지 명령 발행이 실패했습니다. **원인:** ROS 문맥이 먼저 종료됐습니다. **해결:** 신호를 직접 처리해 0 속도를 발행한 뒤 노드를 닫습니다.

## 테스트

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon test --packages-select opencv_pkg --event-handlers console_direct+
colcon test-result --test-result-base build/opencv_pkg --verbose
```
