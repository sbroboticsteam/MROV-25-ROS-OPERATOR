import time
import serial

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
            0.001,
            self.read_serial
        )

        self.get_logger().info("Teleop Serial Reader Started")

    def read_serial(self):

        try:
            line = self.ser.readline().decode('utf-8').strip()
            if not line:
                return
            parts = line.split('|')
            if len(parts) != 3:
                return
            ssi = list(map(float,parts[0].split(',')))
            mag = list(map(float,parts[1].split(',')))
            btn = float(parts[2])

            data = ssi + mag + [btn]
            msg = Float32MultiArray()
            msg.data = data
            self.pub.publish(msg)
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