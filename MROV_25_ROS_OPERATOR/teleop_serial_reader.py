import time
import serial
import struct

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32MultiArray
from std_msgs.msg import Int32



class TeleopSerialReader(Node):

    def __init__(self):
        super().__init__("teleop_serial_reader")

        self.ser = serial.Serial(
            "/dev/ttyACM0",
            115200,
            timeout=1
        )

        # Arduino Uno resets when the serial port opens
        time.sleep(2.0)

        # Throw away anything sent during reset
        self.ser.reset_input_buffer()

        self.pub = self.create_publisher(
            Float32MultiArray,
            "teleop_arm_controller",
            10
        )

        self.timer = self.create_timer(
            0.05,
            self.read_serial
        )

        self.get_logger().info("Teleop Serial Reader Started")

    def read_serial(self):
        try:
            data = self.ser.read(1)
            if data != b'\xAA':
                # self.get_logger().info(f"missed header")
                return
            
            data = self.ser.read(1)
            if data != b'\xFF':
                # self.get_logger().info(f"missed 2nd header")
                return

            msg_len = struct.unpack("<B",self.ser.read(1))
            self.get_logger().info(f"msg_len:{msg_len[0]}")
            payload = self.ser.read(msg_len[0])
            self.get_logger().info(f"payload size:{len(payload)}")
            encoder_values = struct.unpack("<5f", payload)
            
            self.get_logger().info(f"teleop debug:{encoder_values}")
            
            
            # line = self.ser.readline().decode('utf-8').strip()
            # if not line:
            #     return
            # parts = line.split('|')
            # if len(parts) != 3:
            #     return
            # ssi = list(map(float,parts[0].split(',')))
            # mag = list(map(float,parts[1].split(',')))
            # btn = float(parts[2])

            # data = ssi + mag + [btn]
            # msg = Float32MultiArray()
            # msg.data = data
            # self.pub.publish(msg)
        except Exception as e:
            self.get_logger().error(str(e))


def main():

    rclpy.init()

    node = TeleopSerialReader()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.ser.close()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()