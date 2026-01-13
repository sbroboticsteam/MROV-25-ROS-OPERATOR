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

        # Map joystick axes to joints
        self.axis_to_joint = {
            0: 0,  # left stick X -> joint 0
            1: 1,  # left stick Y -> joint 1
        }

        self.joint_commands = [0.0, 0.0]

    def joy_callback(self, msg: Joy):
        for axis_idx, joint_idx in self.axis_to_joint.items():
            if axis_idx < len(msg.axes):
                self.joint_commands[joint_idx] = round(msg.axes[axis_idx], 3)

        cmd_msg = Float64MultiArray()
        cmd_msg.data = self.joint_commands
        self.publisher_.publish(cmd_msg)

        self.get_logger().info(f'Joint commands: {cmd_msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = JoyToController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
