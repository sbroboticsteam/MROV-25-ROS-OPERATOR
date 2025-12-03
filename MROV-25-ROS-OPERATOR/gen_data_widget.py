"""
Widget to display if theres a leak in the E-Box
Author: Tyerone Chen
Create Date: 11/19/2025
Last Update: 11/19/2025
"""
# imports
import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from std_msgs.msg import String
from python_qt_binding.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from python_qt_binding.QtCore import Signal, Slot

class GenDataWidget(QWidget):
    # Consts
    SUB_TO = 'rov/data' # E-Box Node
    # Vars
    data_signal = Signal(str)
    def __init__(self, node_instance):
        super().__init__()
        #Nde setup
        self.node = node_instance
        #widget setup
        layout = QVBoxLayout()
        self.data_label = QLabel("No Data Recieved...")
        self.data_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.data_label)
        self.setLayout(layout)
        # Stylesheet stuff
        self.setStyleSheet("""
            QWidget {
                border: 1px solid #454d55;
                border-radius: 5px;
                padding: 5px;
                margin: 5px;
            }
            QLabel {
            }
        """)
        # Sub Connection
        self.subscription = self.node.create_subscription(String, self.SUB_TO, self.callback, 10)
        self.data_signal.connect(self.update_data_label)
        pass
    # callback
    def callback(self, msg):
        text = f"String Data: {msg}"
        self.data_signal.emit(text)
        pass
    #Slot thingy
    @Slot(str)
    def update_data_label(self, text):
        self.data_label.setText(text)
    # shutdown process
    def shutdown(self):
        if hasattr(self, 'sub') and self.sub:
            self.node.destroy_subscription(self.sub)
        if hasattr(self, 'subscription') and self.subscription:
            self.node.destroy_subscription(self.subscription)

class GenDataPlugin(Plugin):
    def __init__(self, context):
        super(GenDataPlugin, self).__init__(context)
        self.setObjectName('GenDataPlugin')
        self.node = context.node
        self.widget = GenDataWidget(self.node)
        context.add_widget(self.widget)
    # shutdown process
    def shutdown_plugin(self):
        self.widget.shutdown()