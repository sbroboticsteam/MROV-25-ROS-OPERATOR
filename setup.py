import os
from setuptools import find_packages, setup
from glob import glob

package_name = 'MROV-25-ROS-OPERATOR' 
module_name = 'mrov_25_ros_operator' #idk if this is the right name?

setup(
    name=package_name,
    version='1.1.1',
    packages=[package_name],
    data_files=[
        ('share/' +package_name+ '/resource', glob('resource/*.xml')), 
        ('share/ament_index/resource_index/packages', ['resource/' +package_name]),
        ('share/' +package_name, ['package.xml']),
        (os.path.join('share', package_name, 'resource'), glob('resource/*.png')),
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
            'simple_simpub = '+module_name+'.simple_simpub:main',
            'simple_campub = '+module_name+'.simple_campub:main',
        ],
        
        'rqt_gui_py.plugins': [
            'GenCameraWidget = '+module_name+'.gen_camera_widget.GenCameraPlugin',
            'GenDataWidget = '+module_name+'.gen_data_widget:GenDataPlugin',
            'LeakSensorWidget = '+module_name+'.leak_sensor_widget.LeakSensorPlugin',
            'MotorDataWidget = '+module_name+'.motor_data_widget.MotorDataPlugin',
            'SpeedDataWidget = '+module_name+'.speed_data_widget.SpeedDataPlugin',
            'ControllerWidget = '+module_name+'.controller_widget.ControllerPlugin'
        ],
    },
)
