"""Launch the mock LaserScan publisher."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Return a launch description for mock scan publishing."""
    return LaunchDescription([
        DeclareLaunchArgument('topic', default_value='/scan'),
        DeclareLaunchArgument('frame_id', default_value='laser'),
        DeclareLaunchArgument('publish_period', default_value='2.0'),
        Node(
            package='lds_mock_ros',
            executable='mock_scan_publisher',
            name='mock_scan_publisher',
            output='screen',
            parameters=[{
                'topic': LaunchConfiguration('topic'),
                'frame_id': LaunchConfiguration('frame_id'),
                'publish_period': LaunchConfiguration('publish_period'),
            }],
        ),
    ])
