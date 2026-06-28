"""
Author: Tyerone Chen
Last Update: 4/21/2026
"""
import json
import rclpy
import os
import socket
from std_msgs.msg import Bool
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
# Boring Pathing Crap
_share_dir = get_package_share_directory('MROV_25_ROS_OPERATOR')
_ws_root = os.path.abspath(os.path.join(_share_dir, '..', '..', '..', '..'))
RES_PATH = os.path.join(_ws_root, 'src', 'MROV-25-ROS-OPERATOR', 'resource')
ASSETS_PATH = os.path.join(RES_PATH, 'float_assets')
os.makedirs(ASSETS_PATH, exist_ok=True)
class FloatSimPub(Node):
    # Consts
    OUTPUT_FILE = 'output.json'
    TIMEOUT = 2.5
    # Calculation Consts becuase ughh
    P_ATM = 101325.0
    RHO = 1025.0
    G = 9.81
    PA_TO_PSI = 0.000145038
    def __init__(self):
        super().__init__('simple_floatpub')
        # Arduino IP Crap
        self.arduino_ip = '192.168.1.100'
        self.arduino_port = 8080
        # Subscriber Setup
        self.signal_sub = self.create_subscription(Bool, '/float/start_signal', self.signal_callback, 10)
        # Output Setup
        self.output_path = os.path.join(ASSETS_PATH, self.OUTPUT_FILE)
        if os.path.exists(self.output_path): # clear out json
            with open(self.output_path, 'w') as file:
                json.dump([], file)
        # Counter Variable Stuff
        self.timer = self.create_timer(1.0, self.poll_ardunio_status)
    #
    def signal_callback(self, msg):
        if msg.data:
            self.get_logger.info('Recieved Send Signal from Widget -- Contacting Ardunio Float')
            self.send_tcp_command("START\n")
    #
    def send_tcp_command(self, cmd):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.TIMEOUT)
                s.connect((self.arduino_ip, self.arduino_port))
                s.sendall(cmd.encode('utf-8'))
                self.get_logger().info(f"Sent: {cmd.strip()}")
        except Exception as ex:
            self.get_logger().error(f"Could not send {cmd.strip()}: {ex}")
    #
    def poll_ardunio_status(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.TIMEOUT)
                s.connect((self.arduino_ip, self.arduino_port))
                self.get_logger().info("Float detected! Requesting mission dump...")
                self.request_full_data(s)
        except (socket.timeout, ConnectionRefusedError, OSError):
            return
    #
    def request_full_data(self, connected_socket):
        try:
            connected_socket.sendall(b"DUMP\n")
            mission_log = []
            file_obj = connected_socket.makefile('r')
            while True:
                line = file_obj.readline()
                if not line: break
                raw_data = json.loads(line.strip())
                if raw_data.get("status") == "END": break
                # only check if it includes time_ms 
                if "time_ms" in raw_data:
                    depth_m = float(raw_data['depth_m'])
                    # do psi calc
                    pressure_pa = self.P_ATM + (self.RHO * self.G * depth_m)
                    pressure_psi = pressure_pa * self.PA_TO_PSI
                    mission_log.append({
                        'company_num': 'EX01',
                        'time': str(raw_data['time_ms']),
                        'pressure': f'{pressure_psi:.2f}',
                        'depth': str(raw_data['depth_m']),
                        'temp': str(raw_data['temp_c']),
                        'state': raw_data['state']
                    })
            if mission_log:
                self.write_to_json(mission_log)
                self.get_logger().info(f'Mission complete. {len(mission_log)} points saved.')
                
        except Exception as ex:
            self.get_logger().error(f'Error during data dump: {ex}')
    #
    def dump_to_json(self, log_data):
        with open(self.output_path, 'w') as file:
            json.dump(log_data, file, indent=4)
        self.get_logger().info(f'Successfully saved - {len(log_data)} - data points from Arduino memory.')
def main(args=None):
    rclpy.init(args=args)
    node = FloatSimPub()
    rclpy.spin(node)
    rclpy.shutdown()
