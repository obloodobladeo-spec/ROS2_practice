"""Run the JSON scan replay node and optionally rosbridge."""

from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from launch import LaunchDescription


def generate_launch_description():
    """Load JSON files into /scan without running the procedural mock node."""
    return LaunchDescription([
        DeclareLaunchArgument('json_dir'),
        DeclareLaunchArgument('publish_period', default_value='2.0'),
        DeclareLaunchArgument('selection_mode', default_value='random'),
        DeclareLaunchArgument('topic', default_value='/scan'),
        DeclareLaunchArgument('start_rosbridge', default_value='true'),
        Node(
            package='lds_json_replay',
            executable='json_scan_publisher',
            name='json_scan_publisher',
            output='screen',
            parameters=[{
                'json_dir': LaunchConfiguration('json_dir'),
                'publish_period': LaunchConfiguration('publish_period'),
                'selection_mode': LaunchConfiguration('selection_mode'),
                'topic': LaunchConfiguration('topic'),
            }],
        ),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(PathJoinSubstitution([
                FindPackageShare('rosbridge_server'),
                'launch',
                'rosbridge_websocket_launch.xml',
            ])),
            condition=IfCondition(LaunchConfiguration('start_rosbridge')),
        ),
    ])
