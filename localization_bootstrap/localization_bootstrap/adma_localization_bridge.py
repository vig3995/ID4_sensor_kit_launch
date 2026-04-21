#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from geometry_msgs.msg import PoseWithCovarianceStamped, TwistWithCovarianceStamped
from nav_msgs.msg import Odometry
from autoware_localization_msgs.msg import KinematicState
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class AdmaLocalizationBridge(Node):
    def __init__(self):
        super().__init__('adma_localization_bridge')

        # Params
        self.declare_parameter('pose_topic', '/localization/gnss_pose_cov')
        self.declare_parameter('twist_topic', '/localization/twist_with_covariance')
        self.declare_parameter('base_link_frame', 'base_link')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('publish_tf', True)
        self.declare_parameter('time_sync_tolerance_ms', 150)  # simple “near-enough” pairing

        self.pose_topic = self.get_parameter('pose_topic').get_parameter_value().string_value
        self.twist_topic = self.get_parameter('twist_topic').get_parameter_value().string_value
        self.base_link = self.get_parameter('base_link_frame').get_parameter_value().string_value
        self.map_frame = self.get_parameter('map_frame').get_parameter_value().string_value
        self.publish_tf = bool(self.get_parameter('publish_tf').value)
        self.tol_ns = int(self.get_parameter('time_sync_tolerance_ms').value * 1e6)

        # IO
        self.sub_pose = self.create_subscription(PoseWithCovarianceStamped, self.pose_topic, self.on_pose, 10)
        self.sub_twist = self.create_subscription(TwistWithCovarianceStamped, self.twist_topic, self.on_twist, 50)

        self.pub_odom = self.create_publisher(Odometry, '/localization/odometry', 10)
        self.pub_state = self.create_publisher(KinematicState, '/localization/kinematic_state', 10)
        self.br = TransformBroadcaster(self) if self.publish_tf else None

        self.last_pose = None
        self.last_twist = None

    def on_pose(self, msg: PoseWithCovarianceStamped):
        """
        if msg.header.frame_id != self.map_frame:
            self.get_logger().warn_once(f'Pose frame_id is {msg.header.frame_id}, expected {self.map_frame}')
        """
        self.last_pose = msg
        self.try_publish()

    def on_twist(self, msg: TwistWithCovarianceStamped):
        """
        if msg.header.frame_id != self.base_link:
            self.get_logger().warn_once(f'Twist frame_id is {msg.header.frame_id}, expected {self.base_link}')
        """
        self.last_twist = msg
        self.try_publish()

    def try_publish(self):
        if self.last_pose is None or self.last_twist is None:
            return
        # naive time matching: accept if close enough
        t_pose = Time.from_msg(self.last_pose.header.stamp).nanoseconds
        t_twist = Time.from_msg(self.last_twist.header.stamp).nanoseconds
        if abs(t_pose - t_twist) > self.tol_ns:
            return

        # 1) /tf map -> base_link
        if self.publish_tf:
            tf = TransformStamped()
            tf.header.stamp = self.last_pose.header.stamp
            tf.header.frame_id = self.map_frame
            tf.child_frame_id = self.base_link
            tf.transform.translation.x = self.last_pose.pose.pose.position.x
            tf.transform.translation.y = self.last_pose.pose.pose.position.y
            tf.transform.translation.z = self.last_pose.pose.pose.position.z
            tf.transform.rotation = self.last_pose.pose.pose.orientation
            self.br.sendTransform(tf)

        # 2) /localization/odometry
        odom = Odometry()
        odom.header = self.last_pose.header
        odom.child_frame_id = self.base_link
        odom.pose = self.last_pose.pose
        # copy twist (already base_link)
        odom.twist.twist = self.last_twist.twist.twist
        odom.twist.covariance = self.last_twist.twist.covariance
        self.pub_odom.publish(odom)

        # 3) /localization/kinematic_state (pose in map, twist in base_link)
        ks = KinematicState()
        ks.header = self.last_pose.header
        ks.child_frame_id = self.base_link
        ks.pose_with_covariance = self.last_pose.pose
        ks.twist_with_covariance = self.last_twist.twist
        self.pub_state.publish(ks)

def main():
    rclpy.init()
    rclpy.spin(AdmaLocalizationBridge())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
