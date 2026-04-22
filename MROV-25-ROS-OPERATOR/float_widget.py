"""
Widget to display if theres a leak in the E-Box
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 4/21/2026
"""
# imports
import json
import pyqtgraph as pg
import os
from rqt_gui_py.plugin import Plugin
from std_msgs.msg import Bool
from python_qt_binding.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel, QPushButton, QScrollArea, QSizePolicy
from python_qt_binding.QtCore import Qt, Signal, Slot, QTimer
from ament_index_python.packages import get_package_share_directory
# Boring Pathing Crap
_share_dir = get_package_share_directory('py_rov_gui')
_ws_root = os.path.abspath(os.path.join(_share_dir, '..', '..', '..', '..'))
RES_PATH = os.path.join(_ws_root, 'src', 'py_rov_gui', 'resource')
ASSETS_PATH = os.path.join(RES_PATH, 'float_assets')
os.makedirs(ASSETS_PATH, exist_ok=True)
# Main Widget
class FloatWidget(QWidget):
    OUTPUT_FILE = 'output.json'
    def __init__(self, node_instance):
        super().__init__()
        self.node = node_instance
        # File Pathing for Json Updates
        self.output_path = os.path.join(ASSETS_PATH, self.OUTPUT_FILE)
        self.last_size = 0
        # Publisher Stuff
        self.start_pub = self.node.create_publisher(Bool, '/float/start_signal',10)
        # Timer stuff
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_file_update)
        self.timer.start(500)
        # Funny Background Thingy
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: #141414;')
        # Button Layout
        self.buttons = {}
        self.buttons['start'] = CustomButton(self, 'Start Float', self.start_float)
        self.button_layout = QHBoxLayout()
        for button in self.buttons.values():
            self.button_layout.addWidget(button)
        # Sidebar Layout
        self.data_scroll = DataScroll(self.node)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.addWidget(self.data_scroll)
        self.sidebar_layout.addLayout(self.button_layout)
        # Graph Setup
        self.graph = GraphWidget(self.node, 250)
        self.graph.float_signal.connect(self.graph.update_graph_data)
        # Main layout setup
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.graph, stretch=2)
        self.main_layout.addLayout(self.sidebar_layout, stretch=1)
        self.setLayout(self.main_layout)
    def check_file_update(self):
        if not os.path.exists(self.output_path): # check if file even gosh darn exists
            return
        curr_size = os.path.getsize(self.output_path)
        if curr_size != self.last_size:
            self.last_size = curr_size
            self.read_update()
    def read_update(self):
        try:
            with open(self.output_path, 'r') as file:
                data = json.load(file)
            if not data:
                return
            latest = data[-1] # will ge the latest data entry
            label_data = [
                latest['company_num'], 
                latest['time'], 
                latest['pressure'], 
                latest['depth']
            ]
            self.data_scroll.update_labels(label_data)
            self.graph.float_signal.emit(float(latest['time']), float(latest['depth']))
        except Exception as ex:
            print(f'Error While Reading JSON File: {ex}')
    def start_float(self):
        msg = Bool()
        msg.data = True
        self.start_pub.publish(msg)
        self.node.get_logger().info("Widget published start signal to simple_floatpub.")
    def shutdown(self):
        pass
# Main Plugin
class FloatPlugin(Plugin):
    def __init__(self, context):
        super(FloatPlugin, self).__init__(context)
        self.setObjectName('FloatPlugin')
        self.node = context.node
        self.widget = FloatWidget(self.node)
        context.add_widget(self.widget)
    def shutdown(self):
        self.widget.shutdown()
# Custom Widgets
class GraphWidget(QWidget):
    float_signal = Signal(float, float) #  -- might have to change later
    def __init__(self, node_instance, min_size):
        super().__init__()
        self.node = node_instance
        # layout setup
        self.setMinimumSize(min_size, min_size)
        self.layout = QVBoxLayout(self)
        # graph Setup
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.setBackground('#282828')
        self.plot_graph.setTitle('Depth vs Time', color = '#ccc', size = '15pt')
        # data setup - x = time, y = depth - might haveto change later so keep note of that
        self.time = []
        self.depth = []
        self.data_line = self.plot_graph.plot(x=self.time, y=self.depth, pen=(0, 255, 255), symbol='x')
        # add to layout
        self.layout.addWidget(self.plot_graph)
    @Slot(float, float)
    def update_graph_data(self, time_data, depth_data):
        self.time.append(time_data)
        self.depth.append(depth_data)
        # update plot data
        self.data_line.setData(self.time, self.depth)
# Data types it'll recieve will be the - team name, float time, pressure, and depth -
class DataScroll(QScrollArea):
    def __init__(self, node_instance):
        super().__init__()
        self.node = node_instance
        # Scroll Area Setup
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("background-color: #1e1e1e; border: none;")
        # Container for the labels
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #1e1e1e;")
        self.setup_labels()
        self.setWidget(self.container)
        # Sub & Signal Setup
    def setup_labels(self):
        # Labels
        min_w = 100
        self.labels = {}
        self.labels['company_num'] = DataLabel(self, min_w, 'Comp Num', '')
        self.labels['time'] = DataLabel(self, min_w, 'Time', 'ms')
        self.labels['pressure'] = DataLabel(self, min_w, 'PSI', 'pa')
        self.labels['depth'] = DataLabel(self, min_w, 'Depth', 'm')
        # Layout
        self.content_layout = QHBoxLayout(self.container)
        for label in self.labels.values():
            self.content_layout.addWidget(label)
        self.content_layout.addStretch()
    @Slot(list)
    def update_labels(self, data):
        list_order = ['company_num', 'time', 'pressure', 'depth']
        for i, key in enumerate(list_order):
            self.labels[key].update_label(data[i])
# Custom Data Label
class DataLabel(QLabel):
    def __init__(self, parent, min_w, name:str, unit:str):
        super().__init__(parent)
        # variables
        self.unit = unit
        self.name = name
        # Rules and Whatever
        self.setWordWrap(True)
        self.setMinimumWidth(min_w)
        self.setFixedWidth(min_w)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # Def Text should always be name:\n
        self.setText(f'{self.name}:\n')
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.setStyleSheet("""
            font-size: 12px;
            color: white;
            background: #282828;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
        """)
    def update_label(self, data):
        casted = data if isinstance(data, str) else str(data)
        prev = self.text()
        self.setText(f'{prev}\n{casted} {self.unit}')
# Custom Button Class
class CustomButton(QPushButton):
    def __init__(self, parent, name, connection):
        super().__init__(parent)
        self.setObjectName(name)
        self.setText(name)
        self.setStyleSheet("""
            font-size: 12px;
            color: white;
            background: #282828;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
        """)
        self.clicked.connect(connection)
