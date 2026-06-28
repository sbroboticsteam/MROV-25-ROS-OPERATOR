"""
A A Connectivity Widget to display the connectivity of important assets
Author: Tyerone Chen
Create Date: 1/26/2026
Last Update: 4/10/2026
"""
# imports
import time
from rqt_gui_py.plugin import Plugin
from rosidl_runtime_py.utilities import get_message
from python_qt_binding.QtWidgets import QLabel, QVBoxLayout, QWidget
from python_qt_binding.QtCore import Signal, Slot, Qt, QTimer
# Main Widget
class ConnectivityWidget(QWidget):
    def __init__(self, node_instance):
        super().__init__()
        self.node = node_instance
        self.labels = []
        # background color setup
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: #141414;')
        # layout setup
        self.layout = QVBoxLayout(self)
        self.init_components()
        self.setLayout(self.layout)
    def init_components(self):
        # Labels Setup
        self.labels.append(ConnectionLabel(self, self.node, 'Leak', '/rov/leak'))
        self.labels.append(ConnectionLabel(self, self.node, 'Controller', '/op/ctrl'))
        self.labels.append(ConnectionLabel(self, self.node, 'Camera #1', '/rov/camera/image_raw'))
        self.labels.append(ConnectionLabel(self, self.node, 'Camera #2', '/rov/camera'))
        self.labels.append(ConnectionLabel(self, self.node, 'Camera #3', '/rov/camera'))
        # add to layout
        for label in self.labels:
            self.layout.addWidget(label)
    def shutdown(self):
        for label in self.labels:
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
    def __init__(self, parent, node_instance, name, sub_topic):
        # 
        super().__init__(parent)
        self.node = node_instance
        self.sub_topic = sub_topic
        self.sub = None
        self.last_msg_time = 0
        # Label Setup
        self.setObjectName(name)
        self.setText(name)
        self.setAlignment(Qt.AlignCenter)
        self.set_connectivity(False)
        # Timer Setup
        self.watchdog = QTimer(self)
        self.watchdog.timeout.connect(self.check_connectivity)
        self.watchdog.start(500)
    # Methods
    def check_connectivity(self):
        pubs = self.node.get_publishers_info_by_topic(self.sub_topic)
        has_publisher = len(pubs) > 0
        is_active = (time.time() - self.last_msg_time) < 2.0
        self.set_connectivity(has_publisher and is_active)
        # Attempt Subscription if not already
        if has_publisher and self.sub is None:
            self.last_msg_time = time.time()
            self.attempt_subscription(pubs[0].topic_type)
    def attempt_subscription(self, type):
        try:
            self.node.get_logger().info(f"Attempting to subscribe to {self.sub_topic} with type {type}")
            msg_class = get_message(type)
            self.sub = self.node.create_subscription(msg_class, self.sub_topic, self.callback, 10)
        except Exception as ex:
            self.node.get_logger().error(f"Failed to subscribe: {str(ex)}")
    # Callback handeler
    def callback(self, msg):
        self.last_msg_time = time.time()
        self.connectivity_signal.emit(True)
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
