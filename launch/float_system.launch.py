import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    #
    middleman_node = Node(
        package='py_rov_gui',
        executable='simple_floatpub',
        name='simple_floatpub',
        output='screen'
    )
    #
    rqt_widget = ExecuteProcess(
        cmd=['rqt', '--standalone', 'py_rov_gui.float_widget.FloatPlugin'],
        output='screen'
    )
    # 
    return LaunchDescription([
        middleman_node,
        rqt_widget
    ])
