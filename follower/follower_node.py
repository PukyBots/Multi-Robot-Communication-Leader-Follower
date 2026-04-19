import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import threading
import serial
import time

class FollowerRobot(Node):
    def __init__(self):
        super().__init__('follower_robot')

        # Connect to Arduino
        try:
            self.serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            self.get_logger().info('Arduino connected!')
        except:
            self.get_logger().error('Arduino not found!')
            self.serial = None

        self.cmd_publisher = self.create_publisher(Twist, '/follower/cmd_vel', 10)

        # Subscribe to leader odometry
        self.odom_subscriber = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)

        # Subscribe to leader cmd_vel directly
        # Why: Simplest way — follower copies exact same commands as leader
        self.cmd_subscriber = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_callback, 10)

        # Leader state
        self.leader_linear_x = 0.0
        self.leader_angular_z = 0.0
        self.last_odom_time = time.time()
        self.ODOM_TIMEOUT = 1.0
        self.last_state = ''

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
        """
        Receives leader's velocity commands from /cmd_vel.
        Why: Instead of calculating position error, follower simply
        mirrors the same commands — simpler and more reliable for
        DC motors without encoders.
        """
        self.leader_linear_x = msg.linear.x
        self.leader_angular_z = msg.angular.z
        self.last_odom_time = time.time()

    def odom_callback(self, msg):
        """
        Receives leader odometry for logging purposes.
        Why: Useful to verify leader is publishing and for
        future improvement with encoder-based following.
        """
        self.last_odom_time = time.time()
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        self.get_logger().info(f'Leader at x={x:.2f} y={y:.2f}')

    def control_loop(self):
        """
        Main control — mirrors leader commands to follower motors.
        Why: Follower has no encoders so position-based following
        is unreliable. Command mirroring gives best results for
        DC motor robots.
        """
        msg = Twist()

        # Stop if leader stopped or disconnected
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

        # Mirror leader commands
        if self.leader_linear_x > 0.1:
            if self.leader_angular_z > 0.2:
                self.send_command('SMOOTH_LEFT')
                state = 'Turning Left'
            elif self.leader_angular_z < -0.2:
                self.send_command('SMOOTH_RIGHT')
                state = 'Turning Right'
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