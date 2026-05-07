"""
A Camera Widget - Used for displaying multiple camera feedss
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 5/6/2026
"""
# importsw
import os
import cv2
import threading 
from datetime import datetime
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.parameter import Parameter
from rqt_gui_py.plugin import Plugin
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import Bool
from cv_bridge import CvBridge
from python_qt_binding.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from python_qt_binding.QtCore import Signal, Slot, Qt
from python_qt_binding.QtGui import QIcon, QImage, QPixmap
from ament_index_python.packages import get_package_share_directory
# Boring Pathing Crap
_share_dir = get_package_share_directory('py_rov_gui')
_ws_root = os.path.abspath(os.path.join(_share_dir, '..', '..', '..', '..'))
RES_PATH = os.path.join(_ws_root, 'src', 'py_rov_gui', 'resource')
ASSETS_PATH = os.path.join(RES_PATH, 'cam_assets')
OUTPUT_PATH = os.path.join(ASSETS_PATH, 'output')
os.makedirs(ASSETS_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)
# Main Camera Widget, holds 3 instances of the GenCamera Widget
class CameraWidget(QWidget):
    # Consts
    def __init__(self, node_instance):
        super().__init__()
        self.node = node_instance
        # background color setup
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: #141414;')
        # Camera Setup
        self.usb_one = GenCameraWidget(self.node, 'USB Camera 1', '/rov/image_raw', True)
        #self.usb_two = GenCameraWidget(self.node, 'USB Camera 2', '/rov/camera/usb1/image', True)
        self.zed_left = GenCameraWidget(self.node, 'ZED Left', '/rov/camera/zed/left/image', True)
        self.zed_right = GenCameraWidget(self.node, 'ZED Right', '/rov/camera/zed/right/image', True)
        #self.cam_front = GenCameraWidget(self.node, '360 Front', '/rov/camera/insta360/front/image', True)
        #self.cam_back = GenCameraWidget(self.node, '360 Back', '/rov/camera/insta360/back/image', True)
        # Main Layout Setup
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.usb_one)
        self.main_layout.addWidget(self.zed_left)
        self.main_layout.addWidget(self.zed_right)
        self.setLayout(self.main_layout)
    # Shutdown func
    def shutdown(self):
        self.usb_one.shutdown()
        #self.usb_two.shutdown()
        self.zed_left.shutdown()
        self.zed_right.shutdown()
        #self.cam_front.shutdown()
        #self.cam_back.shutdown()
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
    PKG_PATH = get_package_share_directory('py_rov_gui')
    # Vars
    image_signal = Signal(QImage)
    # Constructor
    def __init__(self, node_instance, camera_name, sub_topic, is_compressed):
        super().__init__()
        # Var
        self.callback_group = ReentrantCallbackGroup() # allows for parallel callbacks
        self.node = node_instance
        # setup
        self.setup_ui(camera_name)
        # Connections
        self.sub_topic = sub_topic # Store this for reference
        self.enable_topic = self.sub_topic.replace('/image', '/enable').replace('/image_raw', '/enable')
        self.enable_pub = self.node.create_publisher(Bool, self.enable_topic, 10)   
        # IMG Vars
        self.image_signal.connect(self.update_image_label)
        self.bridge = CvBridge()
        self.is_compressed = is_compressed
        self.sub = self.node.create_subscription(CompressedImage, sub_topic, self.callback, 10, callback_group=self.callback_group) if is_compressed else self.node.create_subscription(Image, sub_topic, self.callback, 10, callback_group=self.callback_group)
        # Recording Variables
        self.fps = 60
        self.output = None
        # Misc Bools
        self.is_processing = False
        self.is_subbed = True
        self.is_recording = False
        self.is_streaming = False
        self.node.get_logger().info(f'{self.name.text()} Feed Started...')
    # UI Setup Related Methods
    def setup_ui(self, camera_name):
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
        self.buttons['play'] = CustomButton(self, 'play_white.png', lambda:self.set_stream(True), 50, 50)
        self.buttons['play'].setStyleSheet('background: green;')
        self.buttons['pause'] = CustomButton(self, 'pause_white.png', lambda:self.set_stream(False), 50, 50)
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
        no_signal_pixmap = QPixmap(os.path.join(ASSETS_PATH, 'no_data.png'))
        if no_signal_pixmap.isNull():
            self.feed.setText('NO SIGNAL - [IMAGE MISSING]')
        else:
            self.feed.setPixmap(no_signal_pixmap)
    # Buttons / Feed Methods
    def set_record(self, state:bool):
        if self.is_recording is state: # to prevent issues with constantly pressing the record button
            return
        self.is_recording = state
        if not self.is_recording and self.output is not None:
            self.output.release()
            self.output = None
            self.node.get_logger().info(f'{self.name.text()} Stopped and Saved Recording.')
        else:
            self.node.get_logger().info(f'{self.name.text()} Started Recording...')
    #
    def set_stream(self, state:bool):
        if self.is_streaming is state: return
        self.is_streaming = state
        
        msg = Bool()
        msg.data = state
        self.enable_pub.publish(msg)
        
        status = "Started" if state else "Stopped"
        self.node.get_logger().info(f'{self.name.text()} Stream {status}.')
    #
    def callback(self, msg):
        if self.is_processing: # trying to remove any backlog of image processes occuring
            return
        try:
            self.is_processing = True
            # get data
            frame_bgr = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8') if self.is_compressed else self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            # Recording Crap, i haveta put it here to refer to the w & h, might move it later but idc
            if self.is_recording and self.output is None:
                # Format Type
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                # Path to Src crap
                output_name = os.path.join(OUTPUT_PATH, f"{self.name.text()}_{datetime.now().strftime('%m_%d_%H_%M_%S')}.mp4")
                os.makedirs(OUTPUT_PATH, exist_ok=True)
                # Create output file
                h, w, _ = frame_bgr.shape
                self.output = cv2.VideoWriter(output_name, fourcc, self.fps, (w, h))
            if self.output is not None:
                self.output.write(frame_bgr)
            # qimage only likes rgb so gotta convert, wololo
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            qimg = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
            # emit data
            self.image_signal.emit(qimg)
        except Exception as ex:
            self.node.get_logger().error(f'ERROR in {self.name.text()} callback: {ex}')
            self.is_processing = False
        finally:
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
    def __init__(self, parent, img_path, connection, w, h):
        super().__init__(parent)
        icon = os.path.join(ASSETS_PATH, img_path)
        self.icon = QIcon(icon)
        self.setIcon(self.icon)
        self.clicked.connect(connection)
        self.og_w = w
        self.og_h = h
        self.setFixedSize(w, h)
