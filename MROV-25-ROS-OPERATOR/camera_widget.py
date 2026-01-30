"""
A Camera Widget - Used for displaying multiple camera feedss
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 1/29/2026
"""
# imports
import os
import cv2
import threading
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from rqt_gui_py.plugin import Plugin
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
from python_qt_binding.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from python_qt_binding.QtCore import Signal, Slot, Qt
from python_qt_binding.QtGui import QIcon, QImage, QPixmap
from ament_index_python.packages import get_package_share_directory
# Main Camera Widget, holds 3 instances of the GenCamera Widget
class CameraWidget(QWidget):
    # Consts
    def __init__(self, node_instance):
        super().__init__()
        self.node = node_instance
        # background color setup
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: #141414;')
        # setup multithreading
        self.executor = MultiThreadedExecutor()
        self.executor.add_node(self.node)
        self.executor_thread = threading.Thread(target=self.executor.spin, daemon=True)
        self.executor_thread.start()
        # Camera Setup
        self.cam_one = GenCameraWidget(self.node, 'Camera 1', '/rov/camera/image_raw')
        self.cam_two = GenCameraWidget(self.node, 'Camera 2', '/rov/camera/image_raw')
        self.cam_three = GenCameraWidget(self.node, 'Camera 3', '/rov/camera/image_raw')
        # Vertical Layout Setup
        self.small_cam_layout = QVBoxLayout()
        self.small_cam_layout.setContentsMargins(0, 0, 0, 0)
        self.small_cam_layout.setSpacing(0)
        self.small_cam_layout.addWidget(self.cam_two)
        self.small_cam_layout.addWidget(self.cam_three)
        # Main Layout Setup
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.cam_one, stretch=2)
        self.main_layout.addLayout(self.small_cam_layout, stretch=1)
        self.setLayout(self.main_layout)
    # Shutdown func
    def shutdown(self):
        self.cam_one.shutdown()
        self.cam_two.shutdown()
        self.cam_three.shutdown()
# Plugin Wrapper
class CameraPlugin(Plugin):
    # Construcgtor
    def __init__(self, context):
        super(CameraPlugin, self).__init__(context)
        self.setObjectName('CameraPlugin')
        self.node = context.node
        self.widget = CameraWidget(self.node)
        context.add_widget(self.widget)
    def shutdown_plugin(self):
        self.widget.shutdown()
# Camera Widget
class GenCameraWidget(QWidget):
    # Consts
    PKG_PATH = get_package_share_directory('py_rov_gui')
    # Vars
    image_signal = Signal(QImage)
    # Constructor
    def __init__(self, node_instance, camera_name, sub_topic):
        super().__init__()
        # Var
        self.is_subbed = False
        self.is_processing = False
        self.callback_group = ReentrantCallbackGroup() # allows for parallel callbacks
        self.node = node_instance
        # setup
        self.setup_ui(sub_topic, camera_name)
        # Connections
        self.image_signal.connect(self.update_image_label)
        self.bridge = CvBridge()
        self.start_feed(sub_topic)
    # UI Setup Related Methods
    def setup_ui(self, sub_topic, camera_name):
        # Labels
        # feed label setup
        self.feed = QLabel()
        self.feed.setScaledContents(True)
        self.feed.setObjectName('frame')
        self.feed.setMinimumSize(1, 1)
        # name label setup
        self.name = QLabel(camera_name)
        self.name.setObjectName('name')
        self.name.setAlignment(Qt.AlignCenter)
        # Btn Setup
        self.buttons = {}
        self.buttons['play'] = CustomButton(self, 'play_white.png', self.PKG_PATH, lambda:self.start_feed(sub_topic), 50, 50)
        self.buttons['play'].setStyleSheet('background: green;')
        self.buttons['pause'] = CustomButton(self, 'pause_white.png', self.PKG_PATH, self.stop_feed, 50, 50)
        self.buttons['pause'].setStyleSheet('background: red;')
        # Button Layout Setup
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.name)
        self.btn_layout.addWidget(self.buttons['play'])
        self.btn_layout.addWidget(self.buttons['pause'])
        # Main Layout Setup
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(self.feed, 1)
        self.setLayout(self.main_layout)
        # Final Toucches
        self.setup_pixmaps()
        self.setStyleSheet("""
            QWidget {
                color: #ccc;
                background: #141414;
                border-radius: 5px;
            }
            QLabel#name {
                background: #282828
            }
        """)
    def setup_pixmaps(self):
        no_signal_pixmap = QPixmap(os.path.join(self.PKG_PATH, 'resource', 'no_data.png'))
        if no_signal_pixmap.isNull():
            self.feed.setText('NO SIGNAL - [IMAGE MISSING]')
        else:
            self.feed.setPixmap(no_signal_pixmap)
    # Buttons / Feed Methods
    def start_feed(self, sub_topic): 
        if not self.is_subbed:
            self.sub = self.node.create_subscription(CompressedImage, sub_topic, self.callback, 10, callback_group=self.callback_group)
            self.is_subbed = True
            self.node.get_logger().info(f'{self.name.text()} Feed Started...')
    def stop_feed(self):
        if self.is_subbed:
            self.node.destroy_subscription(self.sub)
            self.sub = None
            self.is_subbed = False
            self.node.get_logger().info(f'{self.name.text()} Feed Stopped...')
    def callback(self, msg):
        if self.is_processing: # trying to remove any backlog of image processes occuring
            return
        try:
            self.is_processing = True
            # haveta convert from bgr to rgb, else pyqt will throw a fit and make everything colorblind
            frame_bgr = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            qimg = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
            self.image_signal.emit(qimg)
        except Exception as ex:
            self.node.get_logger().error(f'ERROR in {self.name.text()} callback: {ex}')
            self.is_processing = False
    @Slot(QImage)
    def update_image_label(self, qimg):
        self.feed.setPixmap(QPixmap.fromImage(qimg))
        self.is_processing = False
    def shutdown(self):
        if hasattr(self, 'sub') and self.sub:
            self.node.destroy_subscription(self.sub)
# Widget Specific Custom Class
class CustomButton(QPushButton):
    def __init__(self, parent, img_path, pkg_path, connection, w, h):
        super().__init__(parent)
        self.icon = QIcon(os.path.join(pkg_path, 'resource', img_path))
        self.setIcon(self.icon)
        self.clicked.connect(connection)
        self.og_w = w
        self.og_h = h
        self.setFixedSize(w, h)
