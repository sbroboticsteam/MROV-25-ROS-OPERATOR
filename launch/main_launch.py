from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        Node(
            package='joy',
            executable='game_controller_node',
            name='controller_1',
            parameters=[{'device_id': 0}],
            remappings=[('/joy', '/joy1')],
        ),

        Node(
            package='joy',
            executable='game_controller_node',
            name='controller_2',
            parameters=[{'device_id': 1}],
            remappings=[('/joy', '/joy2')],
        ),

        Node(
            package='MROV_25_ROS_OPERATOR',
            executable='joy_to_controller',
            name='joy_to_controller',
            output='screen'
        ),

    ])