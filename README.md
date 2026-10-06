# ROS 2 실습: LDS 모의 주행과 OpenCV 차선 추종

ROS 2 Humble에서 TurtleBot3를 움직이는 실습 모음입니다. 센서 데이터 생성, 원격 주행, MySQL 저장·CSV 추출, Gazebo 카메라 차선 추종을 각각 별도 패키지로 관리합니다. 기존 `cpp_pubsub` 실습도 이 작업 공간에 포함되어 있습니다.

| 경로 | 역할 |
| --- | --- |
| [`src/lds_mock_ros`](src/lds_mock_ros/README.md) | 무작위 360점 라이다 모의 데이터와 rosbridge 실행 |
| [`src/lds02_dataset`](src/lds02_dataset) | JSON 형식 라이다 모의 데이터 1,000개 |
| [`src/lds_json_replay`](src/lds_json_replay/README.md) | JSON을 `/mock_scan` 또는 `/scan`으로 재생 |
| [`src/lds_remote`](src/lds_remote/README.md) | `roslibpy` 주행, MySQL 저장, 361열 CSV 추출 |
| [`src/opencv_pkg`](src/opencv_pkg/README.md) | Waffle Pi 카메라로 노란선 추종 |

## 기본 준비

`turtlebot3_ws`에는 `turtlebot3_gazebo`가 빌드되어 있어야 합니다. 이 작업 공간의 ROS 패키지는 다음과 같이 빌드합니다.

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select lds_mock_ros lds_json_replay opencv_pkg --symlink-install
source install/setup.bash
```

원격 주행 프로그램은 별도 가상 환경을 사용합니다.

```bash
cd ~/ros2_ws/src/lds_remote
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 문제 → 원인 → 해결

아래는 실습 중 실제로 확인한 문제입니다. 명령은 해당 프로그램의 README에도 정리했습니다.

### 1. launch 실행 시 `'str' object has no attribute 'describe_sub_entities'`

- **문제:** `ros2 launch`가 시작되지 않았습니다.
- **원인:** `LaunchDescription([...])`에 Gazebo 실행 액션 대신 패키지 경로 문자열을 넣었습니다.
- **해결:** `IncludeLaunchDescription`으로 만든 실행 액션을 목록에 넣습니다. 예: `LaunchDescription([circle_node, start_gazebo])`.

### 2. `LDS_DB_USER`와 `LDS_DB_PASSWORD`가 없다는 오류

- **문제:** 새 터미널에서 `lds_remote.drive`가 DB 연결 전에 종료됐습니다.
- **원인:** 환경 변수는 새 터미널로 자동 전달되지 않았습니다.
- **해결:** DB 사용자는 기본값 `rosuser`를 사용하고, 비밀번호가 없으면 화면에 표시하지 않고 입력받도록 고쳤습니다. DB를 사용하지 않는 주행 시험에는 `--no-db`를 붙입니다.

### 3. `RosTimeoutError: Failed to connect to ROS`

- **문제:** DB 비밀번호 입력 후 `roslibpy` 연결이 10초 만에 실패했습니다.
- **원인:** Gazebo는 실행 중이었지만 WebSocket 포트 `9090`의 rosbridge가 없었습니다.
- **해결:** 별도 터미널에서 `ros2 launch lds_mock_ros real_bridge.launch.py`를 실행합니다. 연결 포트가 다르면 주행 명령에 `--ros-port`를 지정합니다.

### 4. JSON 재생을 실행해도 Gazebo가 열리지 않음

- **문제:** `json_replay.launch.py`를 실행했는데 JSON 발행과 rosbridge만 시작됐습니다.
- **원인:** 해당 launch 파일에는 Gazebo 실행 액션이 없습니다.
- **해결:** 로봇과 월드도 함께 띄우려면 `json_gazebo.launch.py`를 사용합니다.

### 5. Gazebo 로봇이 벽에 부딪힘

- **문제:** `--scan-topic /mock_scan`으로 주행할 때 Gazebo 벽을 피하지 못했습니다.
- **원인:** `/mock_scan`은 파일에서 재생한 값이라 Gazebo의 현재 장애물 위치와 무관합니다. 발행 주기도 2초였습니다.
- **해결:** Gazebo 장애물에 반응하려면 실제 라이다 `/scan`을 구독합니다. 기본 안전 거리를 `0.75 m`, 직진 속도를 `0.07 m/s`로 조정하고 전방 양쪽 모서리도 검사하도록 고쳤습니다.

### 6. 실제 `/scan`을 받으면 `float(None)` 오류

- **문제:** 주행 프로그램이 모든 스캔을 무효로 판단하고 정지했습니다.
- **원인:** Gazebo 라이다의 `+inf` 거리값이 rosbridge의 JSON 메시지에서는 `null`로 전달됐습니다.
- **해결:** `null`을 라이다의 `range_max`로 변환하도록 고쳤습니다.

### 7. 저장 시각이 1970년으로 표시됨

- **문제:** Gazebo 주행 기록의 `when` 값이 1970년으로 보였습니다.
- **원인:** Gazebo 센서 메시지의 시각은 시뮬레이션 시작 후 경과 시간입니다.
- **해결:** 시뮬레이션 시각이면 실제 UTC 시각으로 저장하도록 고쳤습니다. 이전에 저장된 행은 자동 변경하지 않았습니다.

### 8. 카메라 영상 토픽은 보이는데 영상이 없음

- **문제:** `/camera/image_raw`가 목록에는 있었지만 영상이 나오지 않았습니다.
- **원인:** 당시 실행한 기본 `burger` 모델에는 카메라가 없고, 토픽은 rqt 구독 때문에 목록에 남아 있었습니다. 발행자는 0개였습니다.
- **해결:** Gazebo를 시작하기 전에 `export TURTLEBOT3_MODEL=waffle_pi`로 카메라 모델을 선택합니다. `ros2 topic info /camera/image_raw`의 발행자 수를 확인합니다.

### 9. 카메라 모델에 라이다가 없는 것처럼 보임

- **문제:** `burger_cam`의 `/scan`을 찾지 못했습니다.
- **원인:** 확인 당시 Gazebo가 종료되어 센서 발행자가 없었습니다. 모델 파일에는 카메라와 라이다가 둘 다 정의되어 있습니다.
- **해결:** Gazebo 실행 상태에서 `ros2 topic info /scan`의 발행자 수를 확인합니다.

### 10. OpenCV 주행 중 노란선이 사라짐

- **문제:** 곡선에서 노란선이 화면 맨 아래로 내려오자 로봇이 정지했습니다.
- **원인:** 최초 검출 범위가 이미지 아래쪽 일부를 제외했습니다.
- **해결:** 이미지 하단까지 검출하고 가까운 노란선과 앞쪽 노란선을 함께 사용합니다. 영상이나 선이 끊기면 안전하게 정지합니다.

### 11. `Ctrl+C` 때 정지 명령 발행 오류

- **문제:** OpenCV 노드 종료 시 ROS 문맥이 먼저 닫혀 마지막 정지 명령 발행이 실패했습니다.
- **원인:** 기본 신호 처리기가 `Ctrl+C`에서 ROS 문맥을 즉시 종료했습니다.
- **해결:** 노드가 신호를 직접 처리하여 0 속도 명령을 보낸 뒤 종료하도록 고쳤습니다.

### 12. DB 조회 형식이 실습 예제와 다름

- **문제:** `test.txt`의 조회문과 CSV 내보내기 코드의 SQL이 달랐습니다.
- **원인:** 처음에는 정렬 조건과 식별자 따옴표를 추가해 작성했습니다.
- **해결:** 내보내기 SQL을 예제와 같은 `SELECT ranges, action FROM lidardata`로 맞췄습니다. JSON 배열을 거리 360열과 액션 1열로 변환합니다.

## 실행 예시

실제 Gazebo 라이다 주행은 `waffle_pi`로 `turtlebot3_world.launch.py`를 실행하고 rosbridge를 시작한 다음, 아래 명령을 사용합니다.

```bash
cd ~/ros2_ws/src/lds_remote
.venv/bin/python -m lds_remote.drive --ros-host localhost --scan-topic /scan --no-db
```

JSON 모드는 [재생 패키지 안내](src/lds_json_replay/README.md), 카메라 차선 추종은 [OpenCV 패키지 안내](src/opencv_pkg/README.md)를 따릅니다. `--no-db`는 MySQL 접속과 INSERT를 모두 생략합니다. 하나의 로봇에 여러 주행 프로그램이 동시에 `/cmd_vel`을 발행하지 않도록 합니다.
