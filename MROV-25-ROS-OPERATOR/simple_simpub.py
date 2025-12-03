"""
Author: Tyerone Chen
Last Update: 12/2/2025
"""
# imports
import math
import random
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String, Float64MultiArray

class SimPublisher(Node):
    # consts
    RANGE_PUB_NAME = 'rov/range'
    DATA_PUB_NAME = 'rov/data'
    LEAK_PUB_NAME = 'rov/leak'
    MOTOR_PUB_NAME = 'rov/motor'
    SPEED_PUB_NAME = 'rov/speed'
    MAX_MOTOR_VAL = 1
    MIN_MOTOR_VAL = -1
    MAX_SPEED_VAL = 100
    MIN_SPEED_VAL = 0

    TIMER_INTERVAL = 0.1
    # vfars
    # constructor
    def __init__(self):
        super().__init__('simple_simpub')
        # publisher creator
        self.range_pub = self.create_publisher(Float32, self.RANGE_PUB_NAME, 10)
        self.data_pub = self.create_publisher(String, self.DATA_PUB_NAME, 10)
        self.leak_pub = self.create_publisher(String, self.LEAK_PUB_NAME, 10)
        self.motor_pub = self.create_publisher(Float64MultiArray, self.MOTOR_PUB_NAME, 10)
        self.speed_pub = self.create_publisher(Float64MultiArray, self.SPEED_PUB_NAME, 10)
        # timer setup
        self.timer = self.create_timer(self.TIMER_INTERVAL, self.timer_callback)
        # logger
        self.get_logger().info(f'Simulation Publisher Node Started...')
        self.counter = 0

    def timer_callback(self):
        # Range Publisher Data
        # Creates a nice ocislation whatever, idk i looked this one up
        sim_range = 50.0 + 40.0 * math.sin(self.counter * 0.1) 
        noise = random.uniform(-1.0, 1.0)
        final_range = sim_range + noise
        range_msg = Float32()
        range_msg.data = final_range
        self.range_pub.publish(range_msg)
        # Data & Leak Display Publisher
        if self.counter % 100 == 0: # should be based off of every second
            # got bored lol
            states = [
                "Good ",
                "Goodn't",
                "UnGood",
                "Not Good"
                ]
            data_msg = String()
            data_msg.data = random.choice(states)
            self.data_pub.publish(data_msg)
            leak_states = [
                "No Leak ", 
                "THERES A LEAK IN THE EBOX"
                ]
            leak_msg = String()
            leak_msg.data = random.choice(leak_states)
            self.leak_pub.publish(leak_msg)
        # Motor publisher
        motor_data = [
            random.uniform(self.MIN_MOTOR_VAL, self.MAX_MOTOR_VAL),
            random.uniform(self.MIN_MOTOR_VAL, self.MAX_MOTOR_VAL),
            random.uniform(self.MIN_MOTOR_VAL, self.MAX_MOTOR_VAL),
            random.uniform(self.MIN_MOTOR_VAL, self.MAX_MOTOR_VAL),
            random.uniform(self.MIN_MOTOR_VAL, self.MAX_MOTOR_VAL),
            random.uniform(self.MIN_MOTOR_VAL, self.MAX_MOTOR_VAL),
            random.uniform(self.MIN_MOTOR_VAL, self.MAX_MOTOR_VAL),
            random.uniform(self.MIN_MOTOR_VAL, self.MAX_MOTOR_VAL)
        ]
        motor_msg = Float64MultiArray()
        motor_msg.data = motor_data
        self.motor_pub.publish(motor_msg)
        # Speed Publisher
        speed_data = [
            random.uniform(self.MIN_SPEED_VAL, self.MAX_SPEED_VAL),
            random.uniform(self.MIN_SPEED_VAL, self.MAX_SPEED_VAL),
            random.uniform(self.MIN_SPEED_VAL, self.MAX_SPEED_VAL)
        ]
        speed_msg = Float64MultiArray()
        speed_msg.data = speed_data
        self.speed_pub.publish(speed_msg)
        # Incrementer
        self.counter += 1
    # shutdown mcgee
    def shutdown(self):
        super().destroy_node()
# main
def main(args=None):
    rclpy.init(args=args)
    sim_pub = SimPublisher()
    rclpy.spin(sim_pub)
    sim_pub.shutdown()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
