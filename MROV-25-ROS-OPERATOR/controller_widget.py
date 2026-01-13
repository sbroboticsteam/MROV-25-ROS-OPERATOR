"""
Widget to display controller inputs, & their binding.
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 1/12/2026
"""
# imports
import os
import rclpy
import json # might remove later depending on the pub
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from std_msgs.msg import String
from python_qt_binding.QtWidgets import QWidget, QLabel
from python_qt_binding.QtGui import QPixmap
from python_qt_binding.QtCore import Signal, Slot, Qt
from ament_index_python.packages import get_package_share_directory
# main widget
class ControllerWidget(QWidget):
    # Consts
    SUB_TO = 'controller_input'
    # Vars
    data_signal = Signal(str)
    # init
    def __init__(self, node_instance):
        super().__init__()
        self.node = node_instance
        self.buttons = {}
        self.sticks = {}
        self.REF_W = 734
        self.REF_H = 490
        self.TOP_MARGIN = 150
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        # Widget Setup
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("ctrl_widget")
        self.controller = QLabel(self)
        self.controller.setObjectName("ctrl")
        self.setStyleSheet("""
        QWidget#ctrl_widget {
            background: #141414;
        }
        QLabel#ctrl {
            background: #141414;
        }
        """) # terrible fix but im wiiging it
        pkg_path = get_package_share_directory('py_rov_gui')
        self.controller.setPixmap(QPixmap(os.path.join(pkg_path, 'resource', 'xbox_controller_base.png')))
        self.controller.setScaledContents(True)
        self.init_components()
        # Sub & Update Crap
        self.data_signal.connect(self.process_data)
        self.subscription = self.node.create_subscription(String, self.SUB_TO, self.callback, 10)
    # methods
    # compomntne init
    def init_components(self):
        pkg_path = get_package_share_directory('py_rov_gui')
        def make_btn(normal, pressed, x, y):
            return XboxButton(
                self,
                os.path.join(pkg_path, 'resource', normal),
                os.path.join(pkg_path, 'resource', pressed),
                x, y
            )
        def make_stick(normal, x, y):
            return XboxStick(
                self,
                os.path.join(pkg_path, 'resource', normal),
                x, y
            )
        # -- BUTTONSSS --
        self.buttons['A'] = make_btn('xbox_button_a.png', 'xbox_button_a_pressed.png', 544, 176)
        self.buttons['B'] = make_btn('xbox_button_b.png', 'xbox_button_b_pressed.png', 592, 128)
        self.buttons['X'] = make_btn('xbox_button_x.png', 'xbox_button_x_pressed.png', 496, 128)
        self.buttons['Y'] = make_btn('xbox_button_y.png', 'xbox_button_y_pressed.png', 544, 80)
        # -- D-PAD -- 
        self.buttons['UP'] = make_btn('xbox_dpad_up.png', 'xbox_dpad_up_pressed.png', 225, 212)
        self.buttons['DOWN'] = make_btn('xbox_dpad_down.png', 'xbox_dpad_down_pressed.png', 225, 275)
        self.buttons['LEFT'] = make_btn('xbox_dpad_left.png', 'xbox_dpad_left_pressed.png', 193, 243)
        self.buttons['RIGHT'] = make_btn('xbox_dpad_right.png', 'xbox_dpad_right_pressed.png', 250, 243)
        # -- MISC BUTTONS --
        # -- TRIGGERS --
        self.buttons['LB'] = make_btn('xbox_lb.png', 'xbox_lb_pressed.png', 140, -80)
        self.buttons['LT'] = make_btn('xbox_lt.png', 'xbox_lt_pressed.png', 140, -146)
        self.buttons['RB'] = make_btn('xbox_rb.png', 'xbox_rb_pressed.png', 500, -80)
        self.buttons['RT'] = make_btn('xbox_rt.png', 'xbox_rt_pressed.png', 500, -146)
        # -- STICKSS -- water release, flint n stel
        self.sticks['L-Outline'] = make_stick('xbox_stick_outline.png', 100, 92)
        self.sticks['L'] = make_stick('xbox_stick.png', 128, 121)
        self.sticks['R-Outline'] = make_stick('xbox_stick_outline.png', 402, 206)
        self.sticks['R'] = make_stick('xbox_stick.png', 430, 235)
    #Resize handaeler oveveride
    def resizeEvent(self, event):
        self.scale = min((self.width() / self.REF_W), (self.height() / self.REF_H))
        # apply scale
        new_w = int(self.REF_W * self.scale)
        total_scaled_h = int(self.REF_H * self.scale)
        self.offset_x = (self.width() - new_w) // 2
        self.offset_y = (self.height() - total_scaled_h) // 2
        base_y = self.offset_y + int(self.TOP_MARGIN * self.scale)
        self.controller.setGeometry(self.offset_x, base_y, new_w, int(self.REF_H * self.scale))
        for btn in self.buttons.values():
            new_x = self.offset_x + int(btn.og_x * self.scale)
            new_y = base_y + int(btn.og_y * self.scale)
            btn.move(new_x, new_y)
            btn.setFixedSize(int(btn.og_w * self.scale), int(btn.og_h * self.scale))
            btn.raise_()
        for stick in self.sticks.values():
            new_x = self.offset_x + int(stick.og_x * self.scale)
            new_y = base_y + int(stick.og_y * self.scale)
            stick.move(new_x, new_y)
            stick.setFixedSize(int(stick.og_w * self.scale), int(stick.og_h * self.scale))
            stick.raise_()
    # Callback
    def callback(self, msg):
        self.value_signal.emit(msg.data)
    # GUI Updates
    @Slot(str)
    def process_data(self, json_str): # i have no clue if this works, but it makes sense that it would? but monkeys paw also idk
        try:
            data = json.loads(json_str)
            for btn in ['A', 'B', ' X', 'Y']:
                if btn in data:
                    self.buttons[btn].set_pressed(data[btn] == 1) # checks if the button is published state is 1 ie active
            max_dist = 25 # change later?
            if 'left-x' in data and 'left-y' in data:
                self.update_stick_pos(self.sticks['L'], data['left-x'], data['left-y'], max_dist)
            if 'right-x' in data and 'right-y' in data:
                self.update_stick_pos(self.sticks['R'], data['right-x'], data['right-y'], max_dist)
        except Exception as ex:
            print(f"| Bad Thing Happend | {ex}")
    def update_stick_pos(self, stick, axis_x, axis_y, max_dist):
        base_x = self.offset_x + int(stick.og_x * self.scale)
        base_y = self.offset_y + int(stick.og_y * self.scale)
        move_x = int(axis_x * max_dist + self.scale)
        move_y = int(axis_y * max_dist + self.scale)
        stick.move(base_x + move_x, base_y + move_y)

    # shutdown
    def shutdown(self):
        if hasattr(self, 'sub') and self.sub:
            self.node.destroy_subscription(self.sub)
        if hasattr(self, 'subscription') and self.subscription:
            self.node.destroy_subscription(self.subscription)
# Plugin
class ControllerPlugin(Plugin):
    def __init__(self, context):
        super(ControllerPlugin, self).__init__(context)
        self.setObjectName('ControllerPlugin')
        self.node = context.node
        self.widget = ControllerWidget(self.node)
        context.add_widget(self.widget)
    # shutdown process
    def shutdown_plugin(self):
        self.widget.shutdown()
# Custom Classes
class XboxButton(QLabel):
    def __init__(self, parent, def_img_path, pressed_img_path, x, y):
        super().__init__(parent)
        self.def_pixmap = QPixmap(def_img_path)
        self.pressed_pixmap = QPixmap(pressed_img_path)
        # var storing
        self.og_x = x
        self.og_y = y
        self.og_w = self.def_pixmap.width()
        self.og_h = self.def_pixmap.height()
        # label config
        self.move(x, y)
        self.setFixedSize(self.def_pixmap.width(), self.def_pixmap.height())
        self.setScaledContents(True)
        self.setStyleSheet("background: transparent;")
        # init states
        self.setPixmap(self.def_pixmap)
        self.is_pressed = False
    def set_pressed(self, pressed:bool):
        if self.is_pressed == pressed:
            return
        self.is_pressed = pressed
        if pressed:
            self.setPixmap(self.pressed_pixmap)
        else:
            self.setPixmap(self.def_pixmap)
class XboxStick(QLabel):
    def __init__(self, parent, img_path, x, y):
        super().__init__(parent)
        self.pixmap = QPixmap(img_path)
        # var storing
        self.og_x = x
        self.og_y = y
        self.og_w = self.pixmap.width()
        self.og_h = self.pixmap.height()
        # label config
        self.move(x, y)
        self.setFixedSize(self.pixmap.width(), self.pixmap.height())
        self.setScaledContents(True)
        self.setStyleSheet("background: transparent;")
        self.setPixmap(self.pixmap)
