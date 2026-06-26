from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='MROV_25_ROS_OPERATOR',
            executable='teleop_arm',
            name='teleop_arm',
            output='screen'
        )

    ])