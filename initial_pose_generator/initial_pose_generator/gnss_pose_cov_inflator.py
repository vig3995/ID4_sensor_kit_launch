#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import PoseWithCovarianceStamped
import numpy as np

# Pose cov order (ROS): x, y, z, roll, pitch, yaw
FLOORS = np.array([1.0, 1.0, 4.0, 0.05, 0.05, 0.02], dtype=float)
# -> σx=σy=1.0 m, σz=2.0 m, σroll=σpitch≈0.22 rad (~12°), σyaw≈0.14 rad (~8°)

class GnssPoseCovInflator(Node):
    def __init__(self):
        super().__init__('gnss_pose_cov_inflator')

        # Latched publisher so late EKF still receives the last pose
        qos = QoSProfile(depth=1)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability  = DurabilityPolicy.TRANSIENT_LOCAL

        self.pub = self.create_publisher(
            PoseWithCovarianceStamped,
            '/localization/gnss_pose_cov_for_ekf', qos
        )
        self.sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/localization/gnss_pose_cov',
            self.on_pose, 10
        )

    def on_pose(self, msg: PoseWithCovarianceStamped):
        out = PoseWithCovarianceStamped()
        out.header = msg.header         # keep stamp + frame_id ("map")
        out.pose   = msg.pose

        # clamp diagonals to floors
        cov = np.array(out.pose.covariance, dtype=float).reshape(6,6)
        cov = 0.5*(cov + cov.T)         # symmetrize
        d = np.diag(cov)
        d = np.maximum(d, FLOORS)
        np.fill_diagonal(cov, d)
        out.pose.covariance = cov.flatten().tolist()

        self.pub.publish(out)

def main():
    rclpy.init()
    rclpy.spin(GnssPoseCovInflator())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
