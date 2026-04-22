import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import serial
import time

class FollowerRobot(Node):
    def __init__(self):
        super().__init__('follower_robot')

        try:
            self.serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            self.get_logger().info('Arduino connected!')
        except:
            self.get_logger().error('Arduino not found!')
            self.serial = None

        self.cmd_publisher = self.create_publisher(Twist, '/follower/cmd_vel', 10)

        self.odom_subscriber = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)

        self.cmd_subscriber = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_callback, 10)

        self.leader_linear_x = 0.0
        self.leader_angular_z = 0.0
        self.last_odom_time = time.time()
        self.ODOM_TIMEOUT = 1.0
        self.last_state = ''
        self.last_printed_x = 0.0
        self.last_printed_y = 0.0

        self.get_logger().info('Follower Robot Started!')
        self.get_logger().info('Waiting for leader /cmd_vel and /odom...')

        self.timer = self.create_timer(0.1, self.control_loop)

    def send_command(self, cmd):
        if self.serial:
            try:
                self.serial.write((cmd + '\n').encode())
            except:
                pass

    def cmd_callback(self, msg):
        self.leader_linear_x = msg.linear.x
        self.leader_angular_z = msg.angular.z
        self.last_odom_time = time.time()

    def odom_callback(self, msg):
        self.last_odom_time = time.time()
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # Only print when position changes significantly
        if abs(x - self.last_printed_x) > 0.05 or abs(y - self.last_printed_y) > 0.05:
            self.get_logger().info(f'Leader at x={x:.2f} y={y:.2f}')
            self.last_printed_x = x
            self.last_printed_y = y

    def control_loop(self):
        msg = Twist()

        time_since_cmd = time.time() - self.last_odom_time
        if time_since_cmd > self.ODOM_TIMEOUT:
            self.send_command('STOP')
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            if self.last_state != 'Leader stopped':
                self.get_logger().info('Leader stopped — follower stopped')
                self.last_state = 'Leader stopped'
            self.cmd_publisher.publish(msg)
            return

        if self.leader_linear_x > 0.1:
            if self.leader_angular_z > 0.2:
                self.send_command('SMOOTH_RIGHT')
                state = 'Turning Right'
            elif self.leader_angular_z < -0.2:
                self.send_command('SMOOTH_LEFT')
                state = 'Turning Left'
            else:
                self.send_command('FORWARD')
                state = 'Moving Forward'
            msg.linear.x = self.leader_linear_x
            msg.angular.z = self.leader_angular_z

        elif self.leader_linear_x < -0.1:
            self.send_command('BACKWARD')
            state = 'Moving Backward'
            msg.linear.x = self.leader_linear_x
            msg.angular.z = 0.0

        else:
            self.send_command('STOP')
            state = 'Stopped'
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        if state != self.last_state:
            self.get_logger().info(state)
            self.last_state = state

        self.cmd_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FollowerRobot()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
