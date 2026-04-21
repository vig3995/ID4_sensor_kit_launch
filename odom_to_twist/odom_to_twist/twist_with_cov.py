#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistWithCovarianceStamped

class OdomToTwist(Node):
    def __init__(self):
        super().__init__('twist_with_cov')
        self.declare_parameter('input/odometry', '/genesys/adma/odometry')
        self.declare_parameter('output/twist_with_covariance', '/localization/twist_with_covariance')

        input_topic  = self.get_parameter('input/odometry').get_parameter_value().string_value
        output_topic = self.get_parameter('output/twist_with_covariance').get_parameter_value().string_value

        self.sub = self.create_subscription(Odometry, input_topic, self.cb, 10)
        self.pub = self.create_publisher(TwistWithCovarianceStamped, output_topic, 10)
        self.get_logger().info(f'Subscribing to: {input_topic}')
        self.get_logger().info(f'Publishing to:  {output_topic}')

    def cb(self, msg: Odometry):
        out = TwistWithCovarianceStamped()
        out.header = msg.header
        out.twist = msg.twist
        self.pub.publish(out)

def main():
    rclpy.init()
    node = OdomToTwist()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
