"""
A A Connectivity Widget to display the connectivity of important assets
Author: Tyerone Chen
Create Date: 1/26/2026
Last Update: 1/26/2026
"""
# imports
import os
import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from std_msgs.msg import Bool
from python_qt_binding.QtWidgets import QLabel, QVBoxLayout, QWidget, QSizePolicy
from python_qt_binding.QtCore import Signal, Slot, Qt
# Main Widget
class ConnectivityWidget(QWidget):
    def __init__(self, node_instance):
        super().__init__()
        self.node = node_instance
        self.labels = {}
        # background color setup
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: #141414;')
        # layout setup
        self.layout = QVBoxLayout(self)
        self.init_components()
        self.setLayout(self.layout)
    def init_components(self):
        # Labels Setup
        self.labels['Controller'] = ConnectionLabel(self, self.node, 'Controller', '/op/ctrl')
        self.labels['Camera #1'] = ConnectionLabel(self, self.node, 'Camera #1', '/rov/camera')
        # add to layout
        for label in self.labels.values():
            self.layout.addWidget(label)
    def shutdown(self):
        for label in self.labels.values():
            label.shutdown()
# Plugin
class ConnectivityPlugin(Plugin):
    def __init__(self, context):
        super(ConnectivityPlugin, self).__init__(context)
        self.setObjectName('ConnectivityPlugin')
        self.node = context.node
        self.widget = ConnectivityWidget(self.node)
        context.add_widget(self.widget)
    def shutdown_plugin(self):
        self.widget.shutdown()
# Custom Connection Label
class ConnectionLabel(QLabel):
    # Consts
    connectivity_signal = Signal(bool)
    def __init__(self, parent, node_instance, name, sub_path):
        super().__init__(parent)
        self.node = node_instance
        # Label setup
        self.setObjectName(name)
        self.setText(name)
        self.setAlignment(Qt.AlignCenter)
        self.set_connectivity(False) # default state
        # signal & sub creation
        self.connectivity_signal.connect(self.set_connectivity)
        self.sub = self.node.create_subscription(Bool, sub_path, self.callback, 10)
    # Callback handeler
    def callback(self, msg):
        self.connectivity_signal.emit(msg.data)
        pass
    @Slot(bool) # putting bool for now
    def set_connectivity(self, state):
        if state: 
            self.setStyleSheet("""
                font-size: 20px;
                color: white;
                background: darkGreen;
                border-radius: 5px;
                padding: 20px;
                margin: 10px;
            """)
        else:
            self.setStyleSheet("""
                font-size: 20px;
                color: white;
                background: darkRed;
                border-radius: 5px;
                padding: 20px;
                margin: 10px;
            """)
    # Shutdown process
    def shutdown(self):
        if hasattr(self, 'sub') and self.sub:
            self.node.destroy_subscription(self.sub)