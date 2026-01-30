"""
Widget to display if theres a leak in the E-Box
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 1/29/2026
"""
# imports
from rqt_gui_py.plugin import Plugin
from std_msgs.msg import Bool, Float64MultiArray# might change later
from python_qt_binding.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel, QPushButton, QScrollArea
from python_qt_binding.QtCore import Signal, Slot, Qt
import pyqtgraph as pg

# Main Widget
class FloatWidget(QWidget):
    def __init__(self, node_instance):
        super().__init__()
        # vars
        self.buttons = []
        self.node = node_instance
        # layout setup
        self.main_layout = QHBoxLayout()
        # Widget Setup
        self.graph = GraphWidget(node_instance, 'float/data')
        # Add widgets to layout
        self.main_layout.addWidget(self.graph)
        self.setLayout(self.main_layout)

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
    float_signal = Signal(float, float) #  -- will have to change later
    def __init__(self, node_instance, sub_topic):
        super().__init__()
        self.node = node_instance
        # layout setup
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
        # subscription setup
        self.float_signal.connect(self.update_graph_data)
        self.sub = self.node.create_subscription(Float64MultiArray, sub_topic, self.callback, 10)
    def callback(self, msg):
        # -- for testing float data is published as [time, depth] will change in the future obv. -- 
        self.float_signal.emit(msg.data[0], msg.data[1])
    @Slot(float, float)
    def update_graph_data(self, time_data, depth_data):
        self.time.append(time_data)
        self.depth.append(depth_data)
        # update plot data
        self.data_line.setData(self.time, self.depth)
    def shutdown(self):
        if hasattr(self, 'sub') and self.sub:
            self.node.destroy_subscription(self.sub)
# Data types it'll recieve will be the - team name, float time, pressure, and depth -
class DataScroll(QWidget):
    data_signal = Signal()
    def __init__(self, node_instance, sub_topic):
        super().__init__()
        self.node = node_instance
        self.labels = []
        # Setup
        self.layout = QVBoxLayout(self)

        # Sub & Signal Setup
        
    def callback(self, msg):
        pass
    @Slot()
    def append_label(self, data):
        pass
    def shutdown(self):
        if hasattr(self, 'sub') and self.sub:
            self.node.destroy_subscription(self.sub)
# The holder for each new data instance, unsure if it'll take too much performance with all of the new instance
# the benefit will be readability, might have to talke to ruthvick or karamat
class DataLabel(QLabel):
    def __init__(self, data): # -- data should be in the format of Team, 
        super().__init__()
        self.setStyleSheet("""
            font-size: 12px;
            color: white;
            background: #282828;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
        """)
        text = '| '
        for msg in data:
            text += (str(msg) + ' |')
        self.setText(text)
# not sute if it'll be a sub or a pub for the 
# -- Note for self, might want to add a textout functionality for the data recieved so that the data can be saved locally to a txt --
# -- Also so that the graphing can happen at any time perhaps, like the graph data is read from the output.txt?
class CustomButton(QPushButton):
    button_signal = Signal(bool)
    def __init__(self, node_instance, pub_topic):
        pass

    def shutdown(self):
        pass
