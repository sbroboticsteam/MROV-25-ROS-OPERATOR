"""
Author: Tyerone Chen
Last Update: 1/29/2026
"""
# imports
import rclpy
import cv2
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
from ament_index_python.packages import get_package_share_directory
class CameraPublisher(Node):
    # Consts
    TOPIC_NAME = '/rov/camera/image_raw'
    TIMER_INTERVAL = 0.0167 # framerate is just 1/fps, so 1/60
    # Constructor
    def __init__(self):
        super().__init__('simple_campub')
        package_name = 'sim_publisher'
        package_share_directory = get_package_share_directory(package_name)
        video_file_name = 'video-test-Goast_Bubber.mp4'
        video_path = f'{package_share_directory}/resource/{video_file_name}'
        self.get_logger().info(f"Attempting to open video at: {video_path}")
        self.pub = self.create_publisher(CompressedImage, self.TOPIC_NAME, 10)
        self.timer = self.create_timer(self.TIMER_INTERVAL, self.timer_callback)
        self.bridge = CvBridge() 
        self.cap = cv2.VideoCapture(video_path) 
        self.capture_failed = False
        if not self.cap.isOpened():
            self.get_logger().error("Couldn't Open video Stream")
            self.capture_failed = True 
        else:
            self.get_logger().info("Publishing Node Started")
    # callback waterver
    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return
        frame_resized = cv2.resize(frame, (640, 480))
        msg = self.bridge.cv2_to_compressed_imgmsg(frame_resized, dst_format='jpeg', )
        self.pub.publish(msg)
    def shutdown(self):
        if self.cap.isOpened():
            self.cap.release()
        super().destroy_node()
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
