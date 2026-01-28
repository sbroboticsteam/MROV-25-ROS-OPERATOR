"""
Widget to display if theres a leak in the E-Box
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 1/27/2026
"""
# imports
import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from std_msgs.msg import Bool, Float64MultiArray# might change later
from python_qt_binding.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel, QPushButton
from python_qt_binding.QtCore import Signal, Slot, Qt
import pyqtgraph as pg

# Main Widget
class FloatWidget(QWidget):
    def __init__(self, node_instance):
        super().__init__()
        # vars
        self.buttons = []
        self.node = node_instance
        # layout setup
        self.main_layout = QHBoxLayout()
        # Widget Setup
        self.graph = GraphWidget(node_instance, '/float/data')
        # Add widgets to layout
        self.main_layout.addWidget(self.graph)
        self.setLayout(self.main_layout)

    def shutdown(self):
        pass
# Main Plugin
class FloatPlugin(Plugin):
    def __init__(self, context):
        super(FloatPlugin, self).__init__(context)
        self.setObjectName('FloatPlugin')
        self.node = context.node
        self.widget = FloatWidget(self.node)
        context.add_widget(self.widget)
    def shutdown(self):
        self.widget.shutdown()
# Custom Widgets
class GraphWidget(QWidget):
    def __init__(self, node_instance, sub_topic):
        super().__init__()
        # layout setup
        self.layout = QVBoxLayout(self)
        # graph Setup
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.setBackground('#282828')
        self.plot_graph.setTitle('Depth vs Time')
        # add data -- testing data right now -- 
        time = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        self.plot_graph.plot(time, temperature)
        # add to layout
        self.layout.addWidget(self.plot_graph)

    def shutdown(self):
        pass
# not sute if it'll be a sub or a pub for the 
class CustomButton(QPushButton):
    def __init__(self, parent, pub_topic, data_type):
        pass

    def shutdown(self):
        pass
