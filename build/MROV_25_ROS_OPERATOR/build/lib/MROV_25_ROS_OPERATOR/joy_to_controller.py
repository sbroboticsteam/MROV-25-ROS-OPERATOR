import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import String
import json

def get_dpad(msg):
    # Try axes first (joy_node style)
    if len(msg.axes) >= 8:
        x = msg.axes[6]
        y = msg.axes[7]

        return {
            "up": y > 0.5,
            "down": y < -0.5,
            "left": x > 0.5,
            "right": x < -0.5,
        }

    # Fallback: button-based (game_controller_node style)
    if len(msg.buttons) >= 16:
        return {
            "up": bool(msg.buttons[11]),
            "down": bool(msg.buttons[12]),
            "left": bool(msg.buttons[13]),
            "right": bool(msg.buttons[14]),
        }

    # Safe default
    return {
        "up": False,
        "down": False,
        "left": False,
        "right": False,
    }
AXIS = {
    "left_x": 0,
    "left_y": 1,
    "right_x": 2,
    "right_y": 3,
    "lt": 4,
    "rt": 5
}

BUTTON = {
    "A": 0,
    "B": 1,
    "X": 2,
    "Y": 3,
    "LB": 4,
    "RB": 5
}

DPAD_AXIS = {
    "x": 6,
    "y": 7
}


def trigger_to_01(v):
    return round(1.0 - ((v + 1.0) / 2.0), 3)


class DualJoyPublisher(Node):

    def __init__(self):
        super().__init__('dual_joy_publisher')

        # Publishers
        self.pub1 = self.create_publisher(
            String,
            '/controller1/full_state',
            10
        )

        self.pub2 = self.create_publisher(
            String,
            '/controller2/full_state',
            10
        )

        # Subscribers
        self.sub1 = self.create_subscription(
            Joy,
            '/joy1',
            lambda msg: self.joy_cb(msg, self.pub1),
            10
        )

        self.sub2 = self.create_subscription(
            Joy,
            '/joy2',
            lambda msg: self.joy_cb(msg, self.pub2),
            10
        )

        self.get_logger().info("Dual controller publisher ready")

    def joy_cb(self, msg: Joy, publisher):
        dpad = get_dpad(msg)
        data = {
            "left_x": round(msg.axes[AXIS["left_x"]], 3),
            "left_y": round(msg.axes[AXIS["left_y"]], 3),
            "right_x": round(msg.axes[AXIS["right_x"]], 3),
            "right_y": round(msg.axes[AXIS["right_y"]], 3),

            "lt": round(-1.0 * msg.axes[AXIS["lt"]], 3),
            "rt": round(-1.0 * msg.axes[AXIS["rt"]], 3),

            "A": bool(msg.buttons[BUTTON["A"]]),
            "B": bool(msg.buttons[BUTTON["B"]]),
            "X": bool(msg.buttons[BUTTON["X"]]),
            "Y": bool(msg.buttons[BUTTON["Y"]]),
            "LB": bool(msg.buttons[BUTTON["LB"]]),
            "RB": bool(msg.buttons[BUTTON["RB"]]),

            "dpad_up": dpad["up"],
            "dpad_down": dpad["down"],
            "dpad_left": dpad["left"],
            "dpad_right": dpad["right"],
        }

        out = String()
        out.data = json.dumps(data)

        publisher.publish(out)


def main(args=None):
    rclpy.init(args=args)

    node = DualJoyPublisher()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()