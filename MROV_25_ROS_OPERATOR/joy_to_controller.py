import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Float64MultiArray


class JoyToController(Node):
    def __init__(self):
        super().__init__('joy_to_controller')

        self.publisher_ = self.create_publisher(
            Float64MultiArray,
            '/arm_controller/commands',
            10
        )

        self.subscription = self.create_subscription(
            Joy,
            '/joy',
            self.joy_callback,
            10
        )

        # Axis mapping: joystick axis index -> command index
        self.axis_map = {
            0: 0,  # left stick X
            1: 1,  # left stick Y
            3: 2,  # right stick X
            4: 3,  # right stick Y
        }

        # 4 outputs (two sticks)
        self.commands = [0.0, 0.0, 0.0, 0.0]

    def joy_callback(self, msg: Joy):
        for axis_idx, cmd_idx in self.axis_map.items():
            if axis_idx < len(msg.axes):
                self.commands[cmd_idx] = round(msg.axes[axis_idx], 3)

        out = Float64MultiArray()
        out.data = self.commands
        self.publisher_.publish(out)

        self.get_logger().info(f'Controller commands: {out.data}')


def main(args=None):
    rclpy.init(args=args)
    node = JoyToController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

