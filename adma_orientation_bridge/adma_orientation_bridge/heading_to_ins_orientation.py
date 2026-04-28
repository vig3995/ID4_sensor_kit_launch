# Import:
# -------
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, String
from geometry_msgs.msg import Quaternion
from autoware_sensing_msgs.msg import GnssInsOrientationStamped

# Function 1:
# -----------
def yaw_to_quat(yaw_rad: float) -> Quaternion:
    # roll = pitch = 0, yaw about Z
    q = Quaternion()
    q.w = math.cos(yaw_rad / 2.0)
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw_rad / 2.0)
    return q


# Class 1:
# --------
class HeadingToInsOrientation(Node):
    def __init__(self):
        super().__init__('heading_to_ins_orientation')
        self.deg = self.declare_parameter('heading_is_degrees', True).value
        self.frame = self.declare_parameter('orientation_frame', 'gnss').value
        
        self.sub = self.create_subscription(Float64, '/genesys/adma/heading', self.cb, 10)
        self.pub = self.create_publisher(GnssInsOrientationStamped, '/sensing/gnss/ins_orientation', 10)
        # self.pub = self.create_publisher(String, '/sensing/gnss/ins_orientation', 10)

    def cb(self, msg: Float64):
        yaw = math.radians(msg.data - 90.0) if self.deg else msg.data

        out = GnssInsOrientationStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = self.frame
        out.orientation.orientation = yaw_to_quat(yaw)
        
        self.pub.publish(out)


# Function 2:
# -----------
def main():
    rclpy.init()
    node = HeadingToInsOrientation()
    rclpy.spin(node)
    rclpy.shutdown()


# Run as a script:
# ----------------
if __name__ == '__main__':
    main()
