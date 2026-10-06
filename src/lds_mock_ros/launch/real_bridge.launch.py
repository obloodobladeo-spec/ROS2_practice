"""Launch only rosbridge for a real robot's existing ROS topics."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Expose existing ROS topics over rosbridge without mock publishers."""
    return LaunchDescription([
        DeclareLaunchArgument('port', default_value='9090'),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(PathJoinSubstitution([
                FindPackageShare('rosbridge_server'),
                'launch',
                'rosbridge_websocket_launch.xml',
            ])),
            launch_arguments={
                'port': LaunchConfiguration('port'),
            }.items(),
        ),
    ])
