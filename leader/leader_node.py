import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import serial
import sys
import tty
import termios
import threading
import math
import time

WHEEL_RADIUS = 0.033
WHEEL_BASE = 0.148
ENCODER_PPR = 390

class LeaderRobot(Node):
    def __init__(self):
        super().__init__('leader_robot')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_publisher = self.create_publisher(Odometry, '/odom', 10)

        try:
            self.serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            self.get_logger().info('Arduino connected!')
        except:
            self.get_logger().error('Arduino not found!')
            self.serial = None

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.last_right = 0
        self.last_left = 0

        self.current_cmd = 'STOP'

        self.get_logger().info('Leader Robot Started!')
        self.get_logger().info('w=forward s=backward a=left d=right q=stop x=exit')

        # Thread to read encoder data from Arduino
        self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
        self.serial_thread.start()

    def read_serial(self):
        while True:
            try:
                if self.serial and self.serial.in_waiting:
                    line = self.serial.readline().decode().strip()
                    if line.startswith('ENC:'):
                        parts = line[4:].split(',')
                        if len(parts) == 2:
                            right = int(parts[0])
                            left = int(parts[1])
                            self.update_odometry(right, left)
            except:
                pass
            time.sleep(0.01)

    def update_odometry(self, right, left):
        # Calculate how much each wheel moved
        delta_right = (right - self.last_right) / ENCODER_PPR * 2 * math.pi * WHEEL_RADIUS
        delta_left = (left - self.last_left) / ENCODER_PPR * 2 * math.pi * WHEEL_RADIUS

        self.last_right = right
        self.last_left = left

        # Calculate robot movement
        delta_distance = (delta_right + delta_left) / 2.0
        delta_theta = (delta_right - delta_left) / WHEEL_BASE

        # Update position
        self.x += delta_distance * math.cos(self.theta)
        self.y += delta_distance * math.sin(self.theta)
        self.theta += delta_theta

        # Publish odometry
        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = 'odom'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = math.sin(self.theta / 2)
        odom.pose.pose.orientation.w = math.cos(self.theta / 2)
        self.odom_publisher.publish(odom)


    def get_key(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return key

    def send_command(self, cmd):
        if self.serial:
            try:
                self.serial.write((cmd + '\n').encode())
            except:
                pass

    def run(self):
        msg = Twist()
        while rclpy.ok():
            key = self.get_key()
            if key == 'w':
                self.current_cmd = 'FORWARD'
                msg.linear.x = 0.5
                msg.angular.z = 0.0
                self.send_command('FORWARD')
                self.get_logger().info('Moving Forward')
            elif key == 's':
                self.current_cmd = 'BACKWARD'
                msg.linear.x = -0.5
                msg.angular.z = 0.0
                self.send_command('BACKWARD')
                self.get_logger().info('Moving Backward')
            elif key == 'a':
                self.current_cmd = 'SMOOTH_LEFT'
                msg.linear.x = 0.3
                msg.angular.z = 0.5
                self.send_command('SMOOTH_LEFT')
                self.get_logger().info('Turning Left')
            elif key == 'd':
                self.current_cmd = 'SMOOTH_RIGHT'
                msg.linear.x = 0.3
                msg.angular.z = -0.5
                self.send_command('SMOOTH_RIGHT')
                self.get_logger().info('Turning Right')
            elif key == 'q':
                self.current_cmd = 'STOP'
                msg.linear.x = 0.0
                msg.angular.z = 0.0
                self.send_command('STOP')
                self.get_logger().info('Stopped')
            elif key == 'x':
                self.send_command('STOP')
                break
            self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = LeaderRobot()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    executor_thread = threading.Thread(target=executor.spin, daemon=True)
    executor_thread.start()
    node.run()
    rclpy.shutdown()


if __name__ == '__main__':
    main()