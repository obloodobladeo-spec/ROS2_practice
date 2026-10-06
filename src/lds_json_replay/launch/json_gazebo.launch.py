"""Start Gazebo TurtleBot3 and drive it from replayed JSON scans."""

from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import (
    AnyLaunchDescriptionSource,
    PythonLaunchDescriptionSource,
)
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from launch import LaunchDescription


def generate_launch_description():
    """Start Gazebo, one Burger, JSON /mock_scan, and rosbridge."""
    gazebo_launch = FindPackageShare('gazebo_ros')
    turtlebot_launch = FindPackageShare('turtlebot3_gazebo')
    world = LaunchConfiguration('world')
    json_dir = LaunchConfiguration('json_dir')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')

    return LaunchDescription([
        DeclareLaunchArgument('json_dir'),
        DeclareLaunchArgument('world', default_value=PathJoinSubstitution([
            turtlebot_launch, 'worlds', 'turtlebot3_world.world',
        ])),
        DeclareLaunchArgument('x_pose', default_value='-2.0'),
        DeclareLaunchArgument('y_pose', default_value='-0.5'),
        DeclareLaunchArgument('bridge_port', default_value='9090'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution([
                gazebo_launch, 'launch', 'gzserver.launch.py',
            ])),
            launch_arguments={'world': world}.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution([
                gazebo_launch, 'launch', 'gzclient.launch.py',
            ])),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution([
                turtlebot_launch, 'launch', 'robot_state_publisher.launch.py',
            ])),
            launch_arguments={'use_sim_time': 'true'}.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution([
                turtlebot_launch, 'launch', 'spawn_turtlebot3.launch.py',
            ])),
            launch_arguments={'x_pose': x_pose, 'y_pose': y_pose}.items(),
        ),
        Node(
            package='lds_json_replay',
            executable='json_scan_publisher',
            name='json_scan_publisher',
            output='screen',
            parameters=[{
                'json_dir': json_dir,
                'topic': '/mock_scan',
                'publish_period': 2.0,
            }],
        ),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(PathJoinSubstitution([
                FindPackageShare('rosbridge_server'),
                'launch',
                'rosbridge_websocket_launch.xml',
            ])),
            launch_arguments={
                'port': LaunchConfiguration('bridge_port'),
            }.items(),
        ),
    ])
