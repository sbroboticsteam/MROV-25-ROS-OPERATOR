"""
Widget to display if theres a leak in the E-Box
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 1/31/2026
"""
# imports
from rqt_gui_py.plugin import Plugin
from .progress_bars_widget import ProgBarsWidget, BarWidget
# plugin class
class SpeedDataPlugin(Plugin):
    # Consts
    SUB_TO = 'rov/speed'
    NUM_OF_BARS = 3
    MOTOR_MIN_VAL = 0
    MOTOR_MAX_VAL = 100
    NAME = 'Speed'
    def __init__(self, context):
        super(SpeedDataPlugin, self).__init__(context)
        self.setObjectName('SpeedDataPlugin')
        self.node = context.node
        self.widget = ProgBarsWidget(self.node, self.SUB_TO, self.NUM_OF_BARS, self.MOTOR_MIN_VAL, self.MOTOR_MAX_VAL, self.NAME)
        context.add_widget(self.widget)
    def shutdown_plugin(self):
        self.widget.shutdown()
