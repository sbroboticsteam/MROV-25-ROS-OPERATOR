import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import String
import json


# Typical Xbox mapping from joy_node
AXIS = {
    "left_x": 0,
    "left_y": 1,
    "right_x": 3,
    "right_y": 4,
    "lt": 2,   # trigger axes often [-1,1]
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
    # convert [-1,1] → [0,1] and invert so pressed = 1
    return round(1.0 - ((v + 1.0) / 2.0), 3)


class JoyToController(Node):

    def __init__(self):
        super().__init__('joy_to_controller')

        self.sub = self.create_subscription(
            Joy,
            '/joy',
            self.joy_cb,
            10
        )

        self.pub = self.create_publisher(
            String,
            '/controller/full_state',
            10
        )

        self.get_logger().info("Full controller publisher ready")

    def joy_cb(self, msg: Joy):

        data = {
            # sticks
            "left_x": round(msg.axes[AXIS["left_x"]], 3),
            "left_y": round(msg.axes[AXIS["left_y"]], 3),
            "right_x": round(msg.axes[AXIS["right_x"]], 3),
            "right_y": round(msg.axes[AXIS["right_y"]], 3),

            # triggers 0→1
            "lt": trigger_to_01(msg.axes[AXIS["lt"]]),
            "rt": trigger_to_01(msg.axes[AXIS["rt"]]),

            # buttons (bool)
            "A": bool(msg.buttons[BUTTON["A"]]),
            "B": bool(msg.buttons[BUTTON["B"]]),
            "X": bool(msg.buttons[BUTTON["X"]]),
            "Y": bool(msg.buttons[BUTTON["Y"]]),
            "LB": bool(msg.buttons[BUTTON["LB"]]),
            "RB": bool(msg.buttons[BUTTON["RB"]]),

            # d-pad (axes → bool)
            "dpad_up": msg.axes[DPAD_AXIS["y"]] > 0.5,
            "dpad_down": msg.axes[DPAD_AXIS["y"]] < -0.5,
            "dpad_left": msg.axes[DPAD_AXIS["x"]] > 0.5,
            "dpad_right": msg.axes[DPAD_AXIS["x"]] < -0.5,
        }

        out = String()
        out.data = json.dumps(data)
        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = JoyToController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
