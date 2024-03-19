import rclpy
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, HistoryPolicy, QoSProfile
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import threading

class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('image_subscriber')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image',
            self.image_callback,
            callback_group=rclpy.callback_groups.ReentrantCallbackGroup(),  # Allows callbacks to run in parallel
            qos_profile=QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.RMW_QOS_POLICY_HISTORY_KEEP_LAST)
)  # Use sensor data QoS profile for frame dropping
        self.bridge = CvBridge()
        self.lock = threading.Lock()  # Ensures that callback doesn't process frames simultaneously

    def image_callback(self, msg):
        with self.lock:  # Attempts to acquire the lock, skips frame if lock is not available
            try:
                cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            except Exception as e:
                self.get_logger().error('Failed to convert image: %r' % (e,))
                return
            
            cv2.imshow("Camera Image", cv_image)
            cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    image_subscriber = ImageSubscriber()
    
    # Run the subscriber node using a multi-threaded executor to allow frame dropping effectively
    executor = rclpy.executors.MultiThreadedExecutor()
    rclpy.spin(image_subscriber, executor=executor)

    # Clean up before shutting down
    image_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()