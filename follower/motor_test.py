import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import time

class MotorTestNode(Node):
    def __init__(self):
        super().__init__('motor_test_node')
        try:
            self.serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            time.sleep(2)
            self.get_logger().info('Arduino connected!')
        except Exception as e:
            self.get_logger().error(f'Arduino not found! {e}')
            self.serial = None

        self.cmd_subscriber = self.create_subscription(
            Twist, '/follower/cmd_vel', self.cmd_callback, 10)
        self.last_state = ''
        self.get_logger().info('Ready! Waiting for ROS2 commands...')

    def send_command(self, cmd):
        if self.serial:
            self.serial.write((cmd + '\n').encode())

    def cmd_callback(self, msg):
        if msg.linear.x > 0:
            new_state = 'FORWARD'
        elif msg.linear.x < 0:
            new_state = 'BACKWARD'
        elif msg.angular.z > 0:
            new_state = 'SMOOTH_LEFT'
        elif msg.angular.z < 0:
            new_state = 'SMOOTH_RIGHT'
        else:
            new_state = 'STOP'

        if new_state != self.last_state:
            self.send_command(new_state)
            self.get_logger().info(f'Sending: {new_state}')
            self.last_state = new_state

def main(args=None):
    rclpy.init(args=args)
    node = MotorTestNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()