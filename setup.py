import os
from setuptools import find_packages, setup
from glob import glob

package_name = 'MROV_25_ROS_OPERATOR' 

setup(
    name=package_name,
    version='1.1.1',
    packages=[package_name],
    data_files=[
        ('share/' +package_name+ '/resource', glob('resource/*.xml')), 
        ('share/ament_index/resource_index/packages', ['resource/' +package_name]),
        ('share/' +package_name, ['package.xml']),
        (os.path.join('share', package_name, 'resource'), glob('resource/*.png')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tyerone chen',
    maintainer_email='tchen11898@gmail.com',
    description='Something Gui Something',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'simple_simpub = '+package_name+'.simple_simpub:main',
            'simple_campub = '+package_name+'.simple_campub:main',
            'simple_floatpub = '+package_name+'.simple_floatpub:main',
            'ros_streamer = '+package_name+'.ros_streamer:main',
        ],
        
        'rqt_gui_py.plugins': [
            'CameraWidget = '+package_name+'.camera_widget.CameraPlugin',
            'GenDataWidget = '+package_name+'.gen_data_widget:GenDataPlugin',
            'LeakSensorWidget = '+package_name+'.leak_sensor_widget.LeakSensorPlugin',
            'MotorDataWidget = '+package_name+'.motor_data_widget.MotorDataPlugin',
            'SpeedDataWidget = '+package_name+'.speed_data_widget.SpeedDataPlugin',
            'ControllerWidget = '+package_name+'.controller_widget.ControllerPlugin'
            'ConnectivityWidget = '+package_name+'.connectivity_widget.ConnectivityPlugin'
            'FloatWidget = '+package_name+'.float_widget.FloatPlugin'
        ],
    },
)
