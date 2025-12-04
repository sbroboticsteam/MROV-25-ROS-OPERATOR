"""
Network Widget to display the connectivity between the ROV & the Operator
"""
# imports
import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from std_msgs.msg import String
from python_qt_binding.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from python_qt_binding.QtCore import Signal, Slot

class NetworkWidget(QWidget):
    pass

class NetworkPlugin(Plugin):
    pass