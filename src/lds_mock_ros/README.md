# LDS 모의 스캔 발행기

ROS 2 Humble 패키지입니다. `sensor_msgs/msg/LaserScan`의 거리값 360개를 무작위로 만들어 기본적으로 2초마다 `/scan`에 발행합니다. 앞·뒤·좌·우 벽까지의 거리를 매번 바꾸므로 주행 로직 연습에 사용할 수 있습니다.

## 빌드

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select lds_mock_ros --symlink-install
source install/setup.bash
```

## 모의 데이터 실행

```bash
ros2 launch lds_mock_ros mock_scan.launch.py
```

원격 PC에서 `roslibpy`로 구독하려면 rosbridge도 함께 실행합니다.

```bash
ros2 launch lds_mock_ros mock_remote.launch.py start_rosbridge:=true
```

rosbridge의 기본 주소는 `ws://<ROS_PC_IP>:9090`입니다. `mock_remote.launch.py`는 기본적으로 발행기만 실행하므로 rosbridge가 필요하면 위와 같이 `start_rosbridge:=true`를 지정해야 합니다.

## 실제 라이다를 사용할 때

Gazebo나 실제 TurtleBot3가 `/scan`을 발행 중이라면 모의 발행기를 실행하지 않습니다. 기존 토픽을 원격 프로그램에 연결하는 rosbridge만 시작합니다.

```bash
ros2 launch lds_mock_ros real_bridge.launch.py
```

모의 스캔의 `frame_id`를 바꿔 시험할 수도 있습니다.

```bash
ros2 launch lds_mock_ros mock_scan.launch.py frame_id:=base_scan
```

동일한 `/scan`에 모의 발행기와 Gazebo 라이다를 동시에 연결하면 데이터 출처가 섞입니다. 주행에 사용할 센서 하나만 선택하세요.
