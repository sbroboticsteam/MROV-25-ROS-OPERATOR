"""
A Generic Camera Widget - For now used for just testing out camera stuff
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 12/2/2025
"""
# imports
import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from python_qt_binding.QtWidgets import QLabel, QVBoxLayout, QWidget, QSizePolicy
from python_qt_binding.QtCore import Signal, Slot 
from python_qt_binding.QtGui import QImage, QPixmap

# Camera Widget Class
class GenCameraWidget(QWidget):
    # Consts
    SUB_TO = '/rov/camera/image_raw'
    # Vars
    image_signal = Signal(QPixmap)
    # Constructor
    def __init__(self, node_instance):
        super().__init__()
        # Custom ROS2 Node Setup
        self.node = node_instance
        # Setup
        self.label = QLabel("Waiting for Camera Data...")
        self.label.setScaledContents(True)
        self.label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        # Style Shit - do later
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
        # Slot Connection
        self.image_signal.connect(self.update_image_label)
        # Sub Conncetion
        self.bridge = CvBridge()
        self.sub = self.node.create_subscription(Image, self.SUB_TO, self.callback, 10)
    # METHODSS
    # callback crap
    def callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            self.image_signal.emit(pixmap)
        except Exception as ex:
            self.node.get_logger().error(f"ERROR in camera callback: {ex}")
        pass
    # Slots
    @Slot(QPixmap)
    def update_image_label(self, pixmap):
        self.label.setPixmap(pixmap)
    # shutdown process
    def shutdown(self):
        if hasattr(self, 'sub') and self.sub:
            self.node.destroy_subscription(self.sub)
        if hasattr(self, 'subscription') and self.subscription:
            self.node.destroy_subscription(self.subscription)


# Plugin Wrapper
class GenCameraPlugin(Plugin):
    # Construcgtor
    def __init__(self, context):
        super(GenCameraPlugin, self).__init__(context)
        self.setObjectName('GenCameraPlugin')
        self.node = context.node
        self.widget = GenCameraWidget(self.node)
        context.add_widget(self.widget)
    def shutdown_plugin(self):
        self.widget.shutdown()