"""
A gstreamer middleman ros2 prublisher, to help interperit gstream messages for the camera gui
Author: Tyerone Chen
Create Date: 4/22/2026
Last Update: 5/7/2026
"""
# imports
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Bool
import cv2
import threading

class RosStreamer(threading.Thread):
    def __init__(self, node, image_topic, pipeline):
        super().__init__(daemon=True)
        self.node = node
        self.image_topic = image_topic
        self.gui_topic = image_topic.replace('/image', '/enable').replace('/image_raw', '/enable')
        self.pipeline = pipeline
        #
        self.is_running = False
        self.kill_signal = False
        self.cap = None
        #
        self.pub = node.create_publisher(CompressedImage, image_topic, 10)
        self.sub = node.create_subscription(Bool, self.gui_topic, self.callback, 10)
        self.node.get_logger().info(f'Streamer Created for: {self.gui_topic}')
    #
    def callback(self, msg):
        self.is_running = msg.data
        status = 'ONLINE' if self.is_running else 'OFFLINE'
        self.node.get_logger().info(f'Camera: {self.image_topic} is now: {status}')
    #
    def run(self):
        while not self.kill_signal:
            if not self.is_running: #
                if self.cap: #
                    self.cap.release()
                    self.cap = None
                threading.Event().wait(0.1) # eep
                continue
            if self.cap is None: #
                self.cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)
                if not self.cap.isOpened():
                    self.node.get_logger().error(f"Failed to open GStreamer for {self.image_topic}")
                    self.is_running = False
                    continue
            #
            ret, frame = self.cap.read()
            if ret:
                success, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                if success:
                        msg = CompressedImage()
                        msg.header.stamp = self.node.get_clock().now().to_msg()
                        msg.format = "jpeg"
                        msg.data = encoded.tobytes()
                        self.pub.publish(msg)
            else:
                threading.Event().wait(0.01)
        # only occurs when the streamer is killed
        if self.cap:
            self.cap.release()
        self.node.get_logger().info(f"Thread:{self.image_topic} has exited")
    #
    def shutdown(self):
        self.kill_signal = True
        self.is_running = False
        self.join(timeout=1.0)

class StreamerManagerNode(Node):
    def __init__(self):
        super().__init__('streamer_manager_node')
        # -- Defines the Necessary Streams to watch for and start and whatever --
        # -- FORMAT INFO -> 'ros_topic': 'source' ! filter/conversion ! sink [props]
        self.config = {
            '/rov/camera/image_raw': 'videotestsrc pattern=smpte ! videoconvert ! appsink',
            '/rov/camera/zed/image': 'udpsrc port=5600 buffer-size=524288 caps="application/x-rtp,media=video,clock-rate=90000,encoding-name=H264,payload=96" ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink',
            '/rov/camera/insta360/front/image': 'videotestsrc pattern=snow ! videoconvert ! appsink',
            '/rov/camera/insta360/back/image': 'videotestsrc pattern=checkers ! videoconvert ! appsink'
        }
        # setup workers for streaming
        self.streamers = {}
        for topic_name, pipeline in self.config.items():
            streamer = RosStreamer(self, topic_name, pipeline)
            self.streamers[topic_name] = streamer
            streamer.start()
    #
    def destroy_node(self):
        self.get_logger().info('Shutting Down Streamer Manager...')
        for streamer in self.streamers.values():
            streamer.shutdown()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = StreamerManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
