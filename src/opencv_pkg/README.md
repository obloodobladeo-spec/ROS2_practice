# Waffle Pi yellow line follower

This standalone ROS 2 package uses the Gazebo Waffle Pi camera to find the
yellow Autorace lane marking with OpenCV. It displays the camera and yellow
mask and publishes steering commands on `/cmd_vel`. If the image or line is
missing, it sends zero velocity. The blue line in the display is the desired
yellow-line position; green shows the nearby line and orange shows the line
farther ahead.

## Build

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select opencv_pkg --symlink-install
```

## Run in two terminals

Stop other `/cmd_vel` publishers, including `lds_remote.drive`, first. In the
Gazebo terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_autorace_2020.launch.py
```

In the OpenCV terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run opencv_pkg opencv_follow
```

Press `q` or `Esc` in the camera window, or `Ctrl+C` in the terminal, to stop.
The node sends a final zero `Twist`. Camera topic: `/camera/image_raw`.
For a terminal without a graphical display, use `--no-display`:

```bash
ros2 run opencv_pkg opencv_follow --no-display
```

Options include `--speed`, `--gain`, `--max-turn`, `--target-fraction`,
`--min-area`, `--image-topic`, and `--cmd-topic`. The defaults are tuned for
the Waffle Pi camera in the installed Autorace 2020 world.
