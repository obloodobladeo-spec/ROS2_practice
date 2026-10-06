# JSON file LaserScan replay

This is a separate input mode for the LDS driving exercise. The original
`src/lds02_dataset/lds02_mock_*.json` files are read and published as
`sensor_msgs/LaserScan` on `/scan` every two seconds. The existing
`lds_remote.drive` program then makes the same driving decision, publishes
`/cmd_vel`, and stores the scan/action in `lds_practice.lidardata`.

No Gazebo lidar data is used in this mode. Do not run this together with the
procedural mock publisher or a Gazebo `/scan` publisher, because they would
publish on the same topic.

## Build and run

From the ROS PC:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select lds_json_replay --symlink-install
source install/setup.bash
ros2 launch lds_json_replay json_replay.launch.py \
  json_dir:=/home/kim/ros2_ws/src/lds02_dataset
```

The launch starts rosbridge on port `9090` by default. In another terminal,
run the existing remote client from `../lds_remote` with `--ros-host localhost`.
It prompts for the database password unless `--no-db` is used.

To replay files in sorted order instead of randomly:

```bash
ros2 launch lds_json_replay json_replay.launch.py \
  json_dir:=/home/kim/ros2_ws/src/lds02_dataset selection_mode:=sequential
```

Use `start_rosbridge:=false` if another rosbridge instance already runs.
Use `publish_period:=2.0` to change the publication interval. Each message
has a fresh ROS timestamp and retains the JSON scan's ranges, intensities,
angle geometry, and range limits.

## Move a Gazebo TurtleBot3 using JSON decisions

The launch above does **not** start Gazebo. For a Gazebo robot that moves from
JSON decisions, first stop that launch, then run this one. It starts Gazebo,
spawns the selected TurtleBot3 model, publishes replayed JSON on `/mock_scan`,
and starts rosbridge.
Gazebo's own lidar remains on `/scan`, so the two sources do not collide.

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
source ~/ros2_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch lds_json_replay json_gazebo.launch.py \
  json_dir:=/home/kim/ros2_ws/src/lds02_dataset
```

On the controller computer, run the driver below. `--no-db` keeps this test
from connecting to MySQL or inserting rows:

```bash
.venv/bin/python -m lds_remote.drive \
  --ros-host localhost --scan-topic /mock_scan --no-db
```

For a custom Gazebo world, pass an absolute SDF world path with
`world:=/path/to/my_world.world`. The world needs space for the robot at
`x_pose` and `y_pose`; these are launch arguments. The robot follows **JSON
scan patterns**, so its decisions do not reflect Gazebo obstacles. For obstacle
avoidance in this already running Gazebo world, keep this launch running and
change the driver to `--scan-topic /scan`. This uses Gazebo's actual lidar.
For future runs without JSON replay, start `turtlebot3_gazebo
turtlebot3_world.launch.py` with `TURTLEBOT3_MODEL=waffle_pi` and start
`lds_mock_ros real_bridge.launch.py` separately.
