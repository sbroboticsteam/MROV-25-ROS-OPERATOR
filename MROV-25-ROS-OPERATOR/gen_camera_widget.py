"""
A Generic Camera Widget - For now used for just testing out camera stuff
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 1/21/2026
"""
# imports
import os
import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from python_qt_binding.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy, QPushButton
from python_qt_binding.QtCore import Signal, Slot, QSize 
from python_qt_binding.QtGui import QIcon, QImage, QPixmap
from ament_index_python.packages import get_package_share_directory

# Camera Widget Class
class GenCameraWidget(QWidget):
    # Consts
    SUB_TO = '/rov/camera/image_raw'
    PKG_PATH = get_package_share_directory('py_rov_gui')
    TIMEOUT_DELAY = 2.5
    # Vars
    image_signal = Signal(QPixmap)
    # Constructor
    def __init__(self, node_instance):
        super().__init__()
        # Consts for Referance
        # 4:3 Ratio, just multiplied by 160, due to the no_data.png og size
        self.REF_W = 640 
        self.REF_H = 480
        # Var
        self.is_subbed = False
        self.scale = 1.0
        # Setup
        self.node = node_instance
        self.setup_ui()
        # Connections
        self.image_signal.connect(self.update_image_label)
        self.bridge = CvBridge()
        self.start_feed()
    # METHODSS
    # UI Setup Related Methods
    def setup_ui(self):
        # Label
        self.feed = QLabel(self)
        self.feed.setScaledContents(True)
        # Btn Setup
        self.buttons = {}
        self.buttons["play"] = CustomButton(self, "play_white.png", self.start_feed, 50, 50, 270, 425)
        self.buttons["play"].setStyleSheet("background: green;")
        self.buttons["pause"] = CustomButton(self, "pause_white.png", self.stop_feed, 50, 50, 320, 425)
        self.buttons["pause"].setStyleSheet("background: red;")
        # Final Toucches
        self.setup_pixmaps()
        self.setStyleSheet("""
            QWidget {
                color: #ccc;
                background: #141414;
                border: 3px solid #282828;
                border-radius: 5px;
                padding: 5px;
                margin: 5px;
            }
        """)
    def setup_pixmaps(self):
        no_signal_pixmap = QPixmap(os.path.join(self.PKG_PATH, 'resource', 'no_data.png'))
        if no_signal_pixmap.isNull():
            self.feed.setText("NO SIGNAL - [IMAGE MISSING]")
        else:
            self.feed.setPixmap(no_signal_pixmap)
        
    # resize overide
    def resizeEvent(self, event):
        self.scale = min((self.width() / self.REF_W), (self.height() / self.REF_H))
        # apply scale
        new_w = int(self.REF_W * self.scale)
        new_h = int(self.REF_H * self.scale)
        offset_x = (self.width() - new_w) // 2
        offset_y = (self.height() - new_h) // 2
        self.feed.setGeometry(offset_x, offset_y, new_w, new_h)
        for btn in self.buttons.values():
            new_x = offset_x + int(btn.og_x * self.scale)
            new_y = offset_y + int(btn.og_y * self.scale)
            btn.move(new_x, new_y)
            btn.setFixedSize(int(btn.og_w * self.scale), int(btn.og_h * self.scale))
            btn.setIconSize(QSize(int(btn.og_w * self.scale * 0.5), int(btn.og_h * self.scale * 0.5)))
            btn.raise_()
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
    # Slots
    @Slot(QPixmap)
    def update_image_label(self, pixmap):
        self.feed.setPixmap(pixmap)
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

# Custom BTN Class
class CustomButton(QPushButton):
    PKG_PATH = get_package_share_directory('py_rov_gui')
    def __init__(self, parent, img_path, connection, w, h, x, y):
        super().__init__(parent)
        self.icon = QIcon(os.path.join(self.PKG_PATH, 'resource', img_path))
        self.setIcon(self.icon)
        self.clicked.connect(connection)
        self.og_x, self.og_y  = x, y
        self.og_w = w
        self.og_h = h
        self.setFixedSize(w, h)
        self.move(x, y)
