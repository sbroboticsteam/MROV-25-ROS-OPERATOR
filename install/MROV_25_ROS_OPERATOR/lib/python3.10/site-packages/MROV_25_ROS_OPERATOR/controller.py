import pygame
import rclpy
from rclpy.node import Node

from std_msgs.msg import String
import json
import sys

xbox_controller_button_dict = {
    "0":"A",
    "1":"B",
    "2":"X",
    "3":"Y"
}
xbox_controller_axis_dict={
    "0":"left-x",
    "1":"left-y",
    "2":"right-x",
    "3":"right-y"
}

class ControllerPublisher(Node):
    def __init__(self, tick_rate):
        self.tick_rate = tick_rate
        super().__init__('controller_publisher')
        self.publisher_ = self.create_publisher(String, 'controller_input', 10)

        self.loop = self.create_timer(self.tick_rate, self.controller_callback)
        self.iter_count = 0


        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        print(f"Detected controller: {self.controller.get_name()}")

    def controller_callback(self):
        msg = String()
        ctrlr_dict = {
            "A":0,
            "B":0,
            "X":0,
            "Y":0,
            "left-x":0,
            "left-y":0,
            "right-x":0,
            "right-y":0
        }

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                button = xbox_controller_button_dict.get(str(event.button))
                ctrlr_dict[button] = 1

            if event.type == pygame.JOYBUTTONUP:
                button = xbox_controller_button_dict.get(str(event.button))
                ctrlr_dict[button] = 0

            if event.type == pygame.JOYAXISMOTION:
                axis = xbox_controller_axis_dict.get(str(event.axis))
                axis_val = round(event.value, 3)
                ctrlr_dict[axis] = axis_val

            #for D-pad input
            if event.type == pygame.JOYHATMOTION:
                pass

            if event.type == pygame.QUIT:
                pygame.quit()

        ctrlr_str = json.dumps(ctrlr_dict)
        msg.data = ctrlr_str
        self.publisher_.publish(msg)
        self.get_logger().info(f"Controller data: {ctrlr_str} at {self.iter_count}")
        self.iter_count += 1

def main(args=None):
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller connected!")
        sys.exit()

    rclpy.init(args=args)

    ctrlr_pub = ControllerPublisher(60)

    rclpy.spin(ctrlr_pub)

    ctrlr_pub.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
