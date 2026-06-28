"""
Widget to display the pwm or what not of the 8 motors in the form of 8 prog bars, will also display if there are any issues w/the motor
Author: Tyerone Chen
Create Date: 11/16/2025
Last Update: 1/31/2026
"""
# imports
from rqt_gui_py.plugin import Plugin
from .progress_bars_widget import ProgBarsWidget, BarWidget
# plugin class
class MotorDataPlugin(Plugin):
    # Consts
    SUB_TO = 'rov/motor'
    NUM_OF_BARS = 8
    MOTOR_MIN_VAL = -1
    MOTOR_MAX_VAL = 1
    NAME = 'Motor'
    def __init__(self, context):
        super(MotorDataPlugin, self).__init__(context)
        self.setObjectName('MotorDataPlugin')
        self.node = context.node
        self.widget = ProgBarsWidget(self.node, self.SUB_TO, self.NUM_OF_BARS, self.MOTOR_MIN_VAL, self.MOTOR_MAX_VAL, self.NAME)
        context.add_widget(self.widget)
    def shutdown_plugin(self):
        self.widget.shutdown()
