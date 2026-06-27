from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        # Joystick nodes
       Node(
            package='joy',
            executable='game_controller_node',
            name='controller_2',
            parameters=[{'device_id': 0}],
            remappings=[('/joy', '/joy1')],
        ),

        # Controller publisher
        Node(
            package='MROV_25_ROS_OPERATOR',
            executable='arm_fallback',
            name='arm_fallback',
            output='screen'
        ),

        # Thruster mixer
        Node(
            package='MROV_25_ROS_ROV',
            executable='rov_input_subscriber',
            name='rov_input_subscriber',
            output='screen'
        ),
        
        # arm ctrl
        Node(
            package='MROV_25_ROS_ROV',
            executable='arm_input_subscriber',
            name='arm_input_subscriber',
            output='screen'
        ),

        # sim mapping 
        Node(
            package='MROV_25_ROS_ROV',
            executable='sim_map',
            name='sim_map',
            output='screen'
        ),
    ])