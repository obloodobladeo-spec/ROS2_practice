"""Launch mock scan publishing and optionally the rosbridge websocket."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Run mock scan publishing and optionally rosbridge_server."""
    start_rosbridge = LaunchConfiguration('start_rosbridge')
    return LaunchDescription([
        DeclareLaunchArgument('start_rosbridge', default_value='false'),
        Node(
            package='lds_mock_ros',
            executable='mock_scan_publisher',
            name='mock_scan_publisher',
            output='screen',
            parameters=[{'topic': '/scan', 'frame_id': 'laser'}],
        ),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(PathJoinSubstitution([
                FindPackageShare('rosbridge_server'),
                'launch',
                'rosbridge_websocket_launch.xml',
            ])),
            condition=IfCondition(start_rosbridge),
        ),
    ])
