"""
Widget to display the pwm or what not of the 8 motors in the form of 8 prog bars, will also display if there are any issues w/the motor
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 1/12/2026
"""
# imports
import rclpy
import rclpy.callback_groups
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from std_msgs.msg import Float64MultiArray
from python_qt_binding.QtWidgets import QWidget, QProgressBar, QLabel, QGridLayout
from python_qt_binding.QtCore import Signal, Slot

# widget calss
class MotorDataWidget(QWidget):
    # Consts
    SUB_TO = 'rov/motor' # what to subscribe to, will change with the use of ip
    NUM_OF_BARS = 8 # Number of bars, so 8 cuz 8 motors duh
    MIN_VAL = 0 # prog bars only display values of 0-100
    MAX_VAL = 100
    MOTOR_MIN_VAL = -1 # actual raw values
    MOTOR_MAX_VAL = 1
    # Vars
    value_signal = Signal(list)
    # Constructor
    def __init__(self, node_instance):
        super().__init__()
        # Node Setup
        self.node = node_instance
        # Widget Setup
        layout = QGridLayout()
        self.bars = [] # Holds ProgBars
        self.value_labels = [] # golds the raw vals
        # Looped setup whatever crap
        for i in range(self.NUM_OF_BARS):
            label = QLabel(f"Motor {i + 1} State:")
            bar = QProgressBar()
            bar.setRange(self.MIN_VAL, self.MAX_VAL)
            bar.setFormat("")
            value_label = QLabel("---")
            value_label.setObjectName(f"motor_value_label_{i}")
            self.value_labels.append(value_label)
            self.bars.append(bar)
            layout.addWidget(label, i, 0)
            layout.addWidget(bar, i, 1)
            layout.addWidget(value_label, i, 2)
        self.setLayout(layout)
        # Styleshit, do later
        self.setStyleSheet("""
            QWidget {
                color: #ccc;
                background: #141414;
                border: 3px solid #282828;
                border-radius: 5px;
                padding: 5px;
                margin: 5px;
            }
            QLabel {
            }
        """)
        # Singal Connection
        self.value_signal.connect(self.update_bars)
        # Sub Connections
        self.subscription = self.node.create_subscription(Float64MultiArray, self.SUB_TO, self.callback,
            10, callback_group=rclpy.callback_groups.ReentrantCallbackGroup())
        pass
    # Methods
    # calcback
    def callback(self, msg):
        self.value_signal.emit(list(msg.data))
    # Slotss
    @Slot(list)
    def update_bars(self, value_list):
        for i, val in enumerate(value_list):
            if i < len(self.bars):
                clamped_val = max(self.MOTOR_MIN_VAL, min(self.MOTOR_MAX_VAL, val))
                display_value = int((clamped_val + 1.0) / 2.0 * 100.0)
                self.bars[i].setValue(display_value)
                self.value_labels[i].setText(f"{clamped_val:.2f}")
    # shuts a down
    def shutdown(self):
        if hasattr(self, 'sub') and self.sub:
            self.node.destroy_subscription(self.sub)
        if hasattr(self, 'subscription') and self.subscription:
            self.node.destroy_subscription(self.subscription)
# plugin class
class MotorDataPlugin(Plugin):
    def __init__(self, context):
        super(MotorDataPlugin, self).__init__(context)
        self.setObjectName('MotorDataPlugin')
        self.node = context.node
        self.widget = MotorDataWidget(self.node)
        context.add_widget(self.widget)
    def shutdown_plugin(self):
        self.widget.shutdown()
