# LDS remote driving practice

This directory is the **remote PC** side of the exercise. It subscribes to
`sensor_msgs/LaserScan` on `/scan` through rosbridge, publishes
`geometry_msgs/Twist` on `/cmd_vel`, inserts each 360-distance scan and chosen
action into MySQL, and exports a 361-column CSV. The ROS PC publisher is in the
separate `../lds_mock_ros` package.

## 1. ROS PC: publish mock scans and run rosbridge

Build `lds_mock_ros` and `rosbridge_server` in the ROS 2 Humble workspace, then:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch lds_mock_ros mock_remote.launch.py start_rosbridge:=true
```

The mock publisher sends one 360-point scan every two seconds. rosbridge listens
on WebSocket port `9090`. If rosbridge is not installed on the ROS PC, install
the Humble `rosbridge_server` package or clone and build the Humble branch of
`https://github.com/RobotWebTools/rosbridge_suite.git`.

## 2. MySQL: create a new practice database

On the machine that will store the scans, run the project schema with a MySQL
administrator account:

```bash
sudo mysql < schema.sql
```

This creates the **new** `lds_practice` database, its `lidardata` table, and
grants the existing local MySQL account `rosuser` SELECT and INSERT access.
The table has `id`, a JSON `ranges` array, a UTC `when` datetime, and `action`.
The existing `rosdb` database is not used. If your MySQL account or host differs,
adjust the GRANT in `schema.sql` before running it.

## 3. Remote PC: install and run

From this `lds_remote` directory, install Python dependencies in an isolated
environment. If `python3 -m venv .venv` is unavailable, install `virtualenv`
with `python3 -m pip install --user virtualenv` and run
`python3 -m virtualenv .venv` instead.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m lds_remote.drive --ros-host <ROS_PC_IP>
```

The database defaults to `rosuser` on `localhost:3306` in `lds_practice`.
When `LDS_DB_PASSWORD` is unset, the program prompts for the MySQL password
without showing it on screen. For unattended runs, set `LDS_DB_PASSWORD` in
the environment. `LDS_DB_USER`, `LDS_DB_NAME`, `LDS_DB_HOST`, and `LDS_DB_PORT`
override the other database defaults.

Use `--ros-host localhost` when both roles run on one computer. If MySQL runs
on a different computer from this Python process, set `LDS_DB_HOST` to that
computer's reachable address and grant the MySQL user access from this host.
The ROS topics can be changed with `--scan-topic` and `--cmd-topic`.
Use `--no-db` to test driving without a MySQL connection or INSERTs.

With the default threshold of `0.75` m and forward speed of `0.07` m/s, the
controller checks the front and both front corners before moving. It rotates
in place toward the more open side when blocked, and stops when both sides are
too close. Invalid or stale scans produce a stop command.
Stop the process with Ctrl+C; it publishes a final zero `Twist`.

## 4. Export the dataset

This command also prompts for the database password when it is unset:

```bash
.venv/bin/python -m lds_remote.export_csv --output lidardata.csv
```

The output has `range_000` through `range_359` plus `action`: exactly 361
columns. `when` is stored in MySQL but intentionally omitted from this training
CSV to match the requested shape.

## 5. Replace mock scans with the real TurtleBot3 lidar

Stop `mock_remote.launch.py`, start the real robot's normal bringup so it
publishes `/scan` as `sensor_msgs/LaserScan`, and run only rosbridge on the ROS
PC:

```bash
ros2 launch lds_mock_ros real_bridge.launch.py
```

Run the **same** remote command from step 3. Its angle conversion uses the
LaserScan `angle_min` and `angle_increment`, so it also handles a real scan that
starts at `-pi` or has a point count other than 360. It normalizes the scan to
360 one-degree bins before driving and storing it.

### Gazebo Waffle Pi with its actual lidar

Use `waffle_pi` and `/scan` for obstacle avoidance in the Gazebo world:

```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

In a second ROS terminal start `ros2 launch lds_mock_ros real_bridge.launch.py`
unless rosbridge is already running. Then start the remote driver:

```bash
.venv/bin/python -m lds_remote.drive --ros-host localhost --scan-topic /scan
```

`/mock_scan` contains JSON replay data unrelated to Gazebo obstacles. Using it
to drive a Gazebo robot can make the robot hit walls. The real Gazebo lidar
publishes `/scan` at approximately 5 Hz.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```
