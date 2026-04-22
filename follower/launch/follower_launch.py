from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='follower_robot',
            executable='follower_node',
            name='follower_node',
            output='screen'
        ),
        ExecuteProcess(
            cmd=['ros2', 'topic', 'echo', '/odom'],
            output='screen'
        )
    ])