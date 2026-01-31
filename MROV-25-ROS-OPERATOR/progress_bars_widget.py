"""
A custom widget to display a # of bars
Author: Tyerone Chen
Create Date: 1/31/2026
Last Update: 1/31/2026
"""
# imports
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import Float64MultiArray, Bool
from python_qt_binding.QtWidgets import QWidget, QProgressBar, QLabel, QHBoxLayout, QVBoxLayout
from python_qt_binding.QtCore import Signal, Slot, Qt
# Main Widget Holder
class ProgBarsWidget(QWidget):
    value_signal = Signal(list)
    # Constructor
    def __init__(self, node_instance, sub_topic, num_of_bars, val_min, val_max, name):
        super().__init__()
        # 
        # Vars
        self.node = node_instance
        self.sub_topic = sub_topic
        self.num_of_bars = num_of_bars
        self.val_min = val_min
        self.val_max = val_max
        self.name = name
        self.bars = []
        self.callback_group = ReentrantCallbackGroup()
        # stylesheet
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            ProgBarsWidget {
                background: #141414;
            }
        """)
        # Widget Setup
        self.layout = QVBoxLayout()
        self.setup_bars()
        self.setLayout(self.layout)
        # Singal Connection
        self.value_signal.connect(self.update_bars)
        # Sub Connections
        self.subscription = self.node.create_subscription(Float64MultiArray, self.sub_topic, self.callback, 10, callback_group=self.callback_group)
        pass
    def setup_bars(self):
        for i in range(self.num_of_bars):
            self.bars.append(BarWidget((f'{self.name} Data #{i}'), self.val_min, self.val_max))
            self.layout.addWidget(self.bars[i])
    # calcback
    def callback(self, msg):
        self.value_signal.emit(list(msg.data))
    # Slotss
    @Slot(list)
    def update_bars(self, value_list):
        for i in range(min(len(value_list), self.num_of_bars)):
            self.bars[i].update_bar(value_list[i])
    # shuts a down
    def shutdown(self):
        if hasattr(self, 'sub') and self.sub:
            self.node.destroy_subscription(self.sub)
        if hasattr(self, 'subscription') and self.subscription:
            self.node.destroy_subscription(self.subscription)
# Custom bar class widget
class BarWidget(QWidget):
    DISPLAY_MIN = 0 # displayed val on the prog bar
    DISPLAY_MAX = 100
    def __init__(self, name, min_val, max_val):
        super().__init__()
        self.motor_min = min_val
        self.motor_max = max_val
        # Setup
        layout = QHBoxLayout()
        self.name_label = QLabel(name)
        self.bar = QProgressBar()
        self.bar.setFormat('')
        self.bar.setRange(self.DISPLAY_MIN, self.DISPLAY_MAX)
        self.value_label = QLabel('---')
        # Stylesheet
        self.setStyleSheet("""
            QLabel {
                color: #ccc;
                background: #282828;
                border-radius: 5px;
                padding: 5px;
                margin: 0px 5px 0px 5px;
            }
            QProgressBar {
            color: #ccc;
                background: #282828;
                border-radius: 5px;
                padding: 5px;
                margin: 0px 5px 0px 5px;
            }
        """)
        # add to layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.bar)
        layout.addWidget(self.value_label)
        self.setLayout(layout)
    @Slot(float)
    def update_bar(self, data):
        clamped_val = max(self.motor_min, min(self.motor_max, data))
        display_val = (clamped_val - self.motor_min) / (self.motor_max - self.motor_min) * 100
        self.bar.setValue(int(display_val))
        self.value_label.setText(f"{clamped_val:.2f}")