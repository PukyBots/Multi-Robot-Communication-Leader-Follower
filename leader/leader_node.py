import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import serial
import sys
import tty
import termios
import threading
import math
import time

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
        self.WHEEL_RADIUS = 0.033
        self.WHEEL_BASE = 0.17
        self.TICKS_PER_REV = 360
        self.current_cmd = 'STOP'

        self.get_logger().info('Leader Robot Started!')
        self.get_logger().info('w=forward s=backward a=left d=right q=stop x=exit')

        if self.serial:
            self.serial_thread = threading.Thread(target=self.read_serial)
            self.serial_thread.daemon = True
            self.serial_thread.start()

    def read_serial(self):
        while True:
            try:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode().strip()
                    if line.startswith('ENC:'):
                        parts = line[4:].split(',')
                        right = int(parts[0])
                        left = int(parts[1])
                        self.update_odometry(right, left)
            except:
                pass

    def update_odometry(self, right, left):
        right_dist = (right / self.TICKS_PER_REV) * 2 * math.pi * self.WHEEL_RADIUS
        left_dist = (left / self.TICKS_PER_REV) * 2 * math.pi * self.WHEEL_RADIUS
        center_dist = (right_dist + left_dist) / 2
        delta_theta = (right_dist - left_dist) / self.WHEEL_BASE

        self.x += center_dist * math.cos(self.theta)
        self.y += center_dist * math.sin(self.theta)
        self.theta += delta_theta

        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = 'odom'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
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
            self.serial.write((cmd + '\n').encode())

    def turn_then_straight(self, direction):
        self.send_command(direction)
        self.current_cmd = direction
        time.sleep(1.5)
        self.send_command('FORWARD')
        self.current_cmd = 'FORWARD'

    def run(self):
        msg = Twist()
        while rclpy.ok():
            key = self.get_key()
            if key == 'w':
                self.current_cmd = 'FORWARD'
                msg.linear.x = 0.5
                msg.angular.z = 0.0
                self.send_command('STOP')
                time.sleep(0.1)
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
                t = threading.Thread(target=self.turn_then_straight, args=('SMOOTH_LEFT',))
                t.daemon = True
                t.start()
                self.get_logger().info('Turning Left then Straight')
            elif key == 'd':
                self.current_cmd = 'SMOOTH_RIGHT'
                msg.linear.x = 0.3
                msg.angular.z = -0.5
                t = threading.Thread(target=self.turn_then_straight, args=('SMOOTH_RIGHT',))
                t.daemon = True
                t.start()
                self.get_logger().info('Turning Right then Straight')
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