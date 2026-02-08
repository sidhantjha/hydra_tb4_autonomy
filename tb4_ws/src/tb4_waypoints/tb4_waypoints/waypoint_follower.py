import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import math
import time

class WaypointFollower(Node):
    def __init__(self):
        super().__init__('waypoint_follower')
        self.cmd_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)


        # Simple scripted motion (L-shaped path)
        self.timer = self.create_timer(0.1, self.control_loop)
        self.start_time = time.time()

    def control_loop(self):
        t = time.time() - self.start_time

        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'

        if t < 5.0:
            cmd.twist.linear.x = 0.2
        elif t < 7.0:
            cmd.twist.angular.z = 0.5
        elif t < 12.0:
            cmd.twist.linear.x = 0.2
        else:
            cmd.twist.linear.x = 0.0
            cmd.twist.angular.z = 0.0

        self.cmd_pub.publish(cmd)

def main():
    rclpy.init()
    node = WaypointFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
