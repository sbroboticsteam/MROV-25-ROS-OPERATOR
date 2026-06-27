from setuptools import find_packages, setup

package_name = 'MROV_25_ROS_OPERATOR'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/main_launch.py', 'launch/sim_launch.py', 'launch/teleop_launch.py', 'launch/fallback_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='karamat',
    maintainer_email='karamathasan420@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
           "controller = MROV_25_ROS_OPERATOR.controller:main",
           "joy_to_controller = MROV_25_ROS_OPERATOR.joy_to_controller:main",
           "teleop_arm = MROV_25_ROS_OPERATOR.teleop_serial_reader:main",
           "arm_fallback = MROV_25_ROS_OPERATOR.arm_fallback:main"
        ],
    },
)
