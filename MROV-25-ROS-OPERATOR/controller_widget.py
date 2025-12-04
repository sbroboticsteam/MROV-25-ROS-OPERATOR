"""
Widget to display if theres a leak in the E-Box
"""
# imports
import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from std_msgs.msg import String
from python_qt_binding.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from python_qt_binding.QtCore import Signal, Slot

class ControllerWidget(QWidget):
    pass

class ControllerPlugin(Plugin):
    pass