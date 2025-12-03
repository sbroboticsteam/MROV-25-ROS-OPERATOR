"""
Author: Tyerone Chen
Last Update: 11/72025
"""
# imports
import rclpy
import cv2
import time
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge # Used for converting image types
from ament_index_python.packages import get_package_share_directory

class CameraPublisher(Node):
    # Vars
    TOPIC_NAME = '/rov/camera/image_raw'
    TIMER_INTERVAL = 0.0175
    
    # Constructor
    def __init__(self):
        super().__init__('simple_campub')
        """ for normal camera stuff?
        self.pub = self.create_publisher(Image, self.TOPIC_NAME, 10)
        self.timer = self.create_timer(self.TIMER_INTERVAL, self.timer_callback)
        self.bridge = CvBridge() 
        # init video capture
        #self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2) # For actual camera
        self.cap = cv2.VideoCapture('video-test-Goast_Bubber.mp4')
        self.capture_failed = False
        """
        # For running mp4s or whatever videos
        package_name = 'sim_publisher'
        package_share_directory = get_package_share_directory(package_name)
        video_file_name = 'video-test-Goast_Bubber.mp4'
        video_path = f'{package_share_directory}/resource/{video_file_name}'
        self.get_logger().info(f"Attempting to open video at: {video_path}")
        self.pub = self.create_publisher(Image, self.TOPIC_NAME, 10)
        self.timer = self.create_timer(self.TIMER_INTERVAL, self.timer_callback)
        self.bridge = CvBridge() 
        self.cap = cv2.VideoCapture(video_path) 
        self.capture_failed = False
        # end of section
        if not self.cap.isOpened(): # chedcker to see if this shit failed becausea sljdaljds
            self.get_logger().error("Couldn't Open video Stream")
            self.capture_failed = True 
        else:
            self.get_logger().info("Publishing Node Started")
            """ For Specifivally V4L2
            time.sleep(0.5)
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().warn("Initial camera read failed - setting capture_failed to True.")
                self.capture_failed = True
            """
    # callback waterver
    def timer_callback(self):
        if self.capture_failed:
            return
        ret, frame = self.cap.read() 
        if not ret:
            self.get_logger().info("Video stream ended, looping...")
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) 
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().warn("Failed to read frame after looping.")
                return
        if ret:
            # Resolution
            target_width = 640
            target_height = 480
            frame_resized = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
            img_msg = self.bridge.cv2_to_imgmsg(frame_resized, encoding="bgr8")
            img_msg.header.stamp = self.get_clock().now().to_msg()
            img_msg.header.frame_id = 'camera_frame'
            self.pub.publish(img_msg) 

    # shutdown thingy
    def shutdown(self):
        if self.cap.isOpened():
            self.cap.release()
        super().destroy_node()
# main
def main(args=None):
    rclpy.init(args=args)
    cam_pub = CameraPublisher()
    
    try:
        rclpy.spin(cam_pub)
    except KeyboardInterrupt:
        pass
    finally:
        cam_pub.shutdown()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
