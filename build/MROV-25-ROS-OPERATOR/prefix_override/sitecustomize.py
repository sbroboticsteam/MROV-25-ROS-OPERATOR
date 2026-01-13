import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/germangiraffe/Documents/Robotics/MROV-25-ROS-OPERATOR/install/MROV-25-ROS-OPERATOR'
