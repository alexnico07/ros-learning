import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # Start the Gazebo simulation from the urdf_example fork
    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('urdf_example'),
                         'launch', 'rsp_sim_gz.launch.py')))

    # Start the joint mover on simulated time so it matches Gazebo's clock
    mover = Node(
        package='my_package',
        executable='joint_mover',
        parameters=[{'use_sim_time': True}],
        output='screen')

    return LaunchDescription([sim, mover])
