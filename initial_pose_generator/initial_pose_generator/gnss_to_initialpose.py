#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import PoseWithCovarianceStamped

TOPICS = [
    '/initialpose3d',
    '/initialpose',
    '/localization/initialpose3d',
    '/localization/initialpose',
    ]

class GnssToInitialpose(Node):
    def __init__(self):
        super().__init__('gnss_to_initialpose')
        qos = QoSProfile(depth=1)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability  = DurabilityPolicy.TRANSIENT_LOCAL  # latch-like
        self.pubs = [self.create_publisher(PoseWithCovarianceStamped, t, qos) for t in TOPICS]

        self.sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/localization/gnss_pose_cov',
            self.on_gnss_pose,
            10
        )
        self.once = False

    def on_gnss_pose(self, msg: PoseWithCovarianceStamped):
        if self.once:
            return
        out = PoseWithCovarianceStamped()
        out.header = msg.header            # frame_id should be "map"
        out.pose   = msg.pose
        for p in self.pubs:
            p.publish(out)
        self.get_logger().info('Published initial pose to: ' + ', '.join(TOPICS))
        self.once = True

def main():
    rclpy.init()
    rclpy.spin(GnssToInitialpose())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
