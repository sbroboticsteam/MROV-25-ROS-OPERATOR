"""
A Generic Camera Widget - For now used for just testing out camera stuff
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 1/12/2026
"""
# imports
import os
import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from python_qt_binding.QtWidgets import QLabel, QVBoxLayout, QWidget, QSizePolicy, QPushButton
from python_qt_binding.QtCore import Signal, Slot 
from python_qt_binding.QtGui import QImage, QPixmap
from ament_index_python.packages import get_package_share_directory

# Camera Widget Class
class GenCameraWidget(QWidget):
    # Consts
    SUB_TO = '/rov/camera/image_raw'
    TIMEOUT_DELAY = 2.5
    # Vars
    image_signal = Signal(QPixmap)
    is_subbed = False
    # Constructor
    def __init__(self, node_instance):
        super().__init__()
        self.REF_W = 4
        self.REF_H = 3
        # Custom ROS2 Node Setup
        self.node = node_instance
        # Setup
        # Labels
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setMinimumSize(self.REF_W, self.REF_H)
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.set_no_signal()
        # Buttons - do later
        self.start_button = QPushButton()
        self.start_button.clicked.connect(self.start_feed)
        self.stop_button = QPushButton()
        self.stop_button.clicked.connect(self.stop_feed)
        #Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        # Style Shit - do later
        self.setStyleSheet("""
            QWidget {
                color: #ccc;
                background: #141414;
                border: 3px solid #282828;
                border-radius: 5px;
                padding: 5px;
                margin: 5px;
            }
            QPushButton {

            }
            QLabel {
            }
        """)
        # Slot Connection
        self.image_signal.connect(self.update_image_label)
        # Sub Conncetion
        self.bridge = CvBridge()
        self.start_feed()
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
    # no signal thing
    def set_no_signal(self):
        pkg_share = get_package_share_directory('py_rov_gui')
        img_path = os.path.join(pkg_share, 'resource', 'no_data.png')
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            self.label.setText("NO SIGNAL - [IMAGE MISSING]")
        else:
            self.label.setPixmap(pixmap)
    # resize overide
    def resizeEvent(self, event):
        scale = min((self.width() / self.REF_W), (self.height() / self.REF_H))
        # apply scale
        new_w = int(self.REF_W * scale)
        new_h = int(self.REF_H * scale)
        self.label.setGeometry((self.width() - new_w) // 2, (self.height() - new_h) // 2, new_w, new_h)
        pass
    # Buttons / Feed Methods
    def start_feed(self): 
        if not self.is_subbed:
            self.sub = self.node.create_subscription(Image, self.SUB_TO, self.callback, 10)
            self.is_subbed = True
            self.node.get_logger().info("Camera Feed Started...")
    def stop_feed(self):
        if self.is_subbed:
            self.node.destroy_subscription(self.sub)
            self.sub = None
            self.is_subbed = False
            self.node.get_logger().info("Camera Feed Stopped...")
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
