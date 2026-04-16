from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        # Joystick node
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen'
        ),

        # Controller publisher
        Node(
            package='MROV-25-ROS-OPERATOR',
            executable='joy_to_controller',
            name='joy_to_controller',
            output='screen'
        ),

        # Thruster mixer
        Node(
            package='MROV-25-ROS-ROV',
            executable='rov_input_subscriber',
            name='rov_input_subscriber',
            output='screen'
        ),

        # Splitter node
        Node(
            package='MROV-25-ROS-ROV',
            executable='splitter',
            name='thruster_splitter',
            output='screen'
        ),
    ])