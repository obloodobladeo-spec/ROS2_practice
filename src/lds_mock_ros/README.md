# lds_mock_ros

ROS 2 Humble package for generating randomized LDS-style laser scans. The node
publishes `sensor_msgs/msg/LaserScan` on `/scan` every two seconds by default.
Each scan contains 360 ranges from a rectangular room whose front, rear, left,
and right wall distances change on every publication.

## Run the mock ROS PC publisher

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lds_mock_ros mock_scan.launch.py
```

To also expose ROS topics through rosbridge WebSocket on port 9090, install
`rosbridge_server` on the ROS PC and run:

```bash
ros2 launch lds_mock_ros mock_remote.launch.py start_rosbridge:=true
```

The `mock_remote.launch.py` file defaults to the publisher only, so it can be
used without rosbridge installed. For a real TurtleBot3, launch the robot's
normal sensor stack instead of the mock publisher; it should publish the same
`/scan` `sensor_msgs/msg/LaserScan` interface. The remote bridge endpoint is
`ws://<ROS_PC_IP>:9090`.

## Use a real TurtleBot3 lidar

On the ROS PC, start the robot's normal bringup so it publishes `/scan`, then
open another sourced terminal and start rosbridge only:

```bash
ros2 launch lds_mock_ros real_bridge.launch.py
```

This launch does not start the mock publisher. It exposes the existing ROS
topics over WebSocket on port 9090. The remote PC can connect to
`ws://<ROS_PC_IP>:9090`.

For mock scans, the `frame_id` parameter defaults to `laser`; set it to match
the actual lidar frame when testing the publisher:

```bash
ros2 launch lds_mock_ros mock_scan.launch.py frame_id:=base_scan
```
