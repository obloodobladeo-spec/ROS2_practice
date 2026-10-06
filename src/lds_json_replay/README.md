# JSON 라이다 스캔 재생

`src/lds02_dataset/lds02_mock_*.json`의 라이다 데이터 1,000개를 `sensor_msgs/LaserScan`으로 발행하는 독립 ROS 2 패키지입니다. 기본 발행 간격은 2초이며 무작위 파일을 선택합니다.

## 빌드

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select lds_json_replay --symlink-install
source install/setup.bash
```

## JSON 데이터만 발행

다음 명령은 JSON 스캔을 `/scan`으로 발행하고 rosbridge를 시작합니다. **Gazebo는 실행하지 않습니다.**

```bash
ros2 launch lds_json_replay json_replay.launch.py \
  json_dir:=$HOME/ros2_ws/src/lds02_dataset
```

파일 이름순으로 재생하려면 `selection_mode:=sequential`을 추가합니다. `publish_period:=2.0`으로 발행 간격을 바꿀 수 있습니다. rosbridge가 이미 켜져 있으면 `start_rosbridge:=false`를 지정하세요.

## Gazebo Waffle Pi와 JSON을 함께 실행

이 모드는 Gazebo와 로봇을 띄우고 JSON 데이터를 `/mock_scan`으로 발행합니다. Gazebo의 실제 라이다 `/scan`도 따로 유지됩니다.

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
source ~/ros2_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch lds_json_replay json_gazebo.launch.py \
  json_dir:=$HOME/ros2_ws/src/lds02_dataset
```

다른 터미널에서 JSON 값에 따른 주행을 확인합니다. `--no-db`는 MySQL 접속과 INSERT를 모두 생략합니다.

```bash
cd ~/ros2_ws/src/lds_remote
.venv/bin/python -m lds_remote.drive \
  --ros-host localhost --scan-topic /mock_scan --no-db
```

기존 rosbridge가 `9090`을 사용 중이라면 launch에 `bridge_port:=9091`을 추가하고 주행 명령에도 `--ros-port 9091`을 추가합니다.

`/mock_scan`은 파일에 저장된 모의 값입니다. **Gazebo의 벽 위치를 반영하지 않습니다.** Gazebo 장애물을 감지하며 주행하려면 같은 Gazebo 실행 상태에서 이전 주행 프로그램을 종료하고 `--scan-topic /scan`으로 다시 실행하세요. 두 주행 프로그램을 동시에 `/cmd_vel`에 연결하지 않습니다.

다른 월드를 사용하려면 launch에 `world:=/절대/경로/my_world.world`를 지정할 수 있습니다. 생성 위치는 `x_pose`와 `y_pose` 인수로 바꿉니다.

## 실제로 겪은 문제

1. **문제:** `json_replay.launch.py`를 실행해도 Gazebo가 안 열렸습니다. **원인:** 이 launch는 스캔 발행과 rosbridge만 포함합니다. **해결:** `json_gazebo.launch.py`를 사용합니다.
2. **문제:** JSON 주행 로봇이 벽을 피하지 못했습니다. **원인:** `/mock_scan`은 Gazebo 장애물과 무관합니다. **해결:** 실제 장애물 회피에는 `/scan`을 사용합니다.
3. **문제:** rosbridge 포트가 이미 사용 중이었습니다. **원인:** 다른 launch가 `9090`을 사용했습니다. **해결:** `bridge_port:=9091`과 주행 프로그램의 `--ros-port 9091`을 함께 지정합니다.
