# 원격 LDS 주행과 MySQL 데이터 추출

`lds_remote`는 ROS 2 패키지가 아닌 원격 Python 프로그램입니다. `roslibpy`로 rosbridge의 `sensor_msgs/LaserScan`을 받아 주행 액션을 결정하고 `geometry_msgs/Twist`를 `/cmd_vel`에 발행합니다. DB 사용 모드에서는 거리값 360개와 액션을 `lds_practice.lidardata`에 저장합니다.

## 설치

```bash
cd ~/ros2_ws/src/lds_remote
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`venv` 명령이 없는 환경에서는 `python3 -m pip install --user virtualenv`를 실행한 뒤 `python3 -m virtualenv .venv`를 사용할 수 있습니다.

## Gazebo의 실제 라이다로 주행

터미널 1에서 TurtleBot3 Gazebo를 시작합니다.

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

터미널 2에서 rosbridge를 시작합니다.

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch lds_mock_ros real_bridge.launch.py
```

터미널 3에서 주행 프로그램을 실행합니다. 아래 명령은 DB를 전혀 사용하지 않습니다.

```bash
cd ~/ros2_ws/src/lds_remote
.venv/bin/python -m lds_remote.drive \
  --ros-host localhost --scan-topic /scan --no-db
```

DB 저장도 원하면 `--no-db`를 빼고 실행합니다. 기본 DB 연결은 `localhost:3306`의 `lds_practice`, 사용자 `rosuser`입니다. `LDS_DB_PASSWORD`가 설정되지 않았다면 시작할 때 비밀번호를 묻습니다. 다른 환경에서는 `LDS_DB_HOST`, `LDS_DB_PORT`, `LDS_DB_NAME`, `LDS_DB_USER`를 지정할 수 있습니다. rosbridge 포트가 `9090`이 아니라면 `--ros-port`를 사용하세요.

기본 안전 거리는 `0.75 m`, 직진 속도는 `0.07 m/s`입니다. 전방과 전방 양쪽 모서리를 검사하고, 막히면 열린 방향으로 제자리 회전합니다. 영상과 관계없는 JSON 모의 스캔 `/mock_scan`으로 Gazebo 벽을 피할 수는 없습니다. 종료할 때 `Ctrl+C`를 누르면 정지 명령을 보냅니다.

## DB 구조와 CSV

DB를 처음 준비할 때만 MySQL 관리자 계정으로 `schema.sql`을 실행합니다. 기존 `rosdb`를 사용하지 않고 별도 `lds_practice`를 만듭니다. `rosuser` 계정은 이미 생성되어 있어야 합니다.

```bash
cd ~/ros2_ws/src/lds_remote
sudo mysql < schema.sql
```

`lidardata`에는 정수 `id`, JSON `ranges`, UTC `when`, 문자열 `action`이 있습니다. 내보내기 프로그램의 조회문은 실습 예제와 같습니다.

```sql
SELECT ranges, action FROM lidardata
```

CSV 파일을 만들려면 다음 명령을 사용합니다.

```bash
.venv/bin/python -m lds_remote.export_csv --output output.csv
```

결과에는 `range_000`부터 `range_359`까지의 거리값 360열과 `action` 1열, 총 361열이 있습니다. `when`은 DB에만 남기고 이 CSV에는 넣지 않습니다. 비밀번호가 환경 변수에 없다면 내보내기 실행 시에도 입력받습니다.

## 자주 겪은 문제

1. **문제:** `RosTimeoutError`. **원인:** rosbridge가 실행되지 않았거나 포트가 다릅니다. **해결:** `real_bridge.launch.py`를 시작하고 `--ros-port`를 확인합니다.
2. **문제:** `float(None)`로 스캔이 무효가 됐습니다. **원인:** rosbridge가 무한 거리값을 JSON `null`로 보냈습니다. **해결:** 현재 코드는 이를 `range_max`로 처리합니다.
3. **문제:** 로봇이 Gazebo 벽에 부딪혔습니다. **원인:** `/mock_scan`은 실제 벽과 무관합니다. **해결:** `--scan-topic /scan`을 사용합니다.
4. **문제:** DB 기록이 1970년이었습니다. **원인:** Gazebo 시뮬레이션 시각을 실제 날짜로 해석했습니다. **해결:** 새 기록에는 실제 UTC 시각을 사용합니다. 이전 행은 자동 수정하지 않습니다.

## 테스트

```bash
.venv/bin/python -m unittest discover -s tests -v
```
