#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

# Joint limits from the URDF (slider in metres, arm in radians)
SLIDER_LIMITS = (0.0, 2.0)
ARM_LIMITS = (0.0, math.pi / 2)


def clamp(value, limits):
    # Keep a command inside [lower, upper] so a bad parameter can't exceed the joint limits
    return max(limits[0], min(limits[1], value))


class JointMover(Node):
    def __init__(self):
        super().__init__('joint_mover')

        # Parameters, so they can be changed at launch or while running (ros2 param set)
        # Each joint moves as: centre + amplitude * sin(2 * pi * frequency * t)
        self.declare_parameter('slider_center', 1.0)
        self.declare_parameter('slider_amplitude', 0.9)
        self.declare_parameter('arm_center', math.pi / 4)
        self.declare_parameter('arm_amplitude', 0.7)
        self.declare_parameter('frequency', 0.2)       # Hz
        self.declare_parameter('publish_rate', 20.0)   # Hz

        # These topics are bridged to the Gazebo joint position controllers
        self.slider_pub = self.create_publisher(Float64, 'slider_joint/cmd_pos', 10)
        self.arm_pub = self.create_publisher(Float64, 'arm_joint/cmd_pos', 10)

        # The node clock follows Gazebo's clock when use_sim_time is true
        self.start_time = self.get_clock().now()

        rate = self.get_parameter('publish_rate').value
        self.timer = self.create_timer(1.0 / rate, self.update)
        self.get_logger().info('Joint mover started')

    def update(self):
        # Seconds since the node started
        t = (self.get_clock().now() - self.start_time).nanoseconds * 1e-9

        # Read the parameters each time, so changes take effect immediately
        freq = self.get_parameter('frequency').value
        wave = math.sin(2.0 * math.pi * freq * t)

        slider = Float64()
        slider.data = clamp(
            self.get_parameter('slider_center').value
            + self.get_parameter('slider_amplitude').value * wave,
            SLIDER_LIMITS)

        arm = Float64()
        arm.data = clamp(
            self.get_parameter('arm_center').value
            + self.get_parameter('arm_amplitude').value * wave,
            ARM_LIMITS)

        self.slider_pub.publish(slider)
        self.arm_pub.publish(arm)


def main(args=None):
    rclpy.init(args=args)
    node = JointMover()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
