"""
Author: Tyerone Chen
Last Update: 3/2/2026
"""
import json
import rclpy
import os
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
# Boring Pathing Crap
_share_dir = get_package_share_directory('py_rov_gui')
_ws_root = os.path.abspath(os.path.join(_share_dir, '..', '..', '..', '..'))
RES_PATH = os.path.join(_ws_root, 'src', 'py_rov_gui', 'resource')
ASSETS_PATH = os.path.join(RES_PATH, 'float_assets')
os.makedirs(ASSETS_PATH, exist_ok=True)
class FloatSimPub(Node):
    # Consts
    OUTPUT_FILE = 'output.json'
    def __init__(self):
        super().__init__('simple_floatpub')
        self.output_path = os.path.join(ASSETS_PATH, self.OUTPUT_FILE)
        if os.path.exists(self.output_path):
            with open(self.output_path, 'w') as file:
                json.dump([], file)
        self.timer = self.create_timer(1.0, self.update_json_data)
        self.counter = 0.0
    def update_json_data(self):
        self.counter += 1.0
        new_entry = {
            "company_num": "EX01",
            "time": str(self.counter),
            "pressure": str(95.0 + (self.counter * 0.1)),
            "depth": str(self.counter * 0.5)
        }
        data = []
        if os.path.exists(self.output_path):
            try:
                with open(self.output_path, 'r') as file:
                    data = json.load(file)
            except (json.JSONDecodeError, ValueError):
                data = []
        data.append(new_entry)

        with open(self.output_path, 'w') as file:
            json.dump(data, file, indent=4)
        self.get_logger().info(f'Updated JSON File at Counter: {self.counter}')
def main(args=None):
    rclpy.init(args=args)
    node = FloatSimPub()
    rclpy.spin(node)
    rclpy.shutdown()