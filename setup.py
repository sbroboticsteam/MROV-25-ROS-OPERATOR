import os
from setuptools import find_packages, setup
from glob import glob

package_name = 'MROV-25-ROS-OPERATOR'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/' +package_name+ '/resource', glob('resource/*.xml')), 
        ('share/ament_index/resource_index/packages', ['resource/' +package_name]),
        ('share/' +package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tyerone',
    maintainer_email='tchen11898@gmail.com',
    description='Something Gui Something',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'rqt_gui_py.plugins': [
            'GenCameraWidget = MROV-25-ROS-OPERATOR.gen_camera_widget.GenCameraPlugin',
            'GenDataWidget = MROV-25-ROS-OPERATOR.gen_data_widget:GenDataPlugin',
            'LeakSensorWidget = MROV-25-ROS-OPERATOR.leak_sensor_widget.LeakSensorPlugin',
            'MotorDataWidget = MROV-25-ROS-OPERATOR.motor_data_widget.MotorDataPlugin',
            'SpeedDataWidget = MROV-25-ROS-OPERATOR.speed_data_widget.SpeedDataPlugin'
        ],
    },
)
