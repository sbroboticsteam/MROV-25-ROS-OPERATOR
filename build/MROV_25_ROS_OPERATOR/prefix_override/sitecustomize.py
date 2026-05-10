import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/germangiraffe/Documents/tester/ros2_ws/src/MROV-25-ROS-OPERATOR/install/MROV_25_ROS_OPERATOR'
