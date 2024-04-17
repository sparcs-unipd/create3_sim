# Copyright 2021 Clearpath Robotics, Inc.
# @author Roni Kreinin (rkreinin@clearpathrobotics.com)

import os

from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, AppendEnvironmentVariable
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='use_sim_time'),
    DeclareLaunchArgument('world', default_value='maze',
                          description='Gz World'),
    DeclareLaunchArgument('gui', default_value='false',
                            description='Enable gui plugin for create3')
]


def generate_launch_description():

    # Directories
    pkg_irobot_create_gz_bringup = get_package_share_directory(
        'irobot_create_gz_bringup')
    pkg_irobot_create_gz_plugins = get_package_share_directory(
        'irobot_create_gz_plugins')
    pkg_irobot_create_description = get_package_share_directory(
        'irobot_create_description')
    pkg_ros_gz_gazebo = get_package_share_directory(
        'ros_gz_sim')

    # Set gz resource path
    gz_resource_path = AppendEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH',
                                               value=[os.path.join(
                                                      pkg_irobot_create_gz_bringup,
                                                      'worlds'), ':' +
                                                      str(Path(
                                                          pkg_irobot_create_description).
                                                          parent.resolve())])

    gz_gui_plugin_path = AppendEnvironmentVariable(name='GZ_GUI_PLUGIN_PATH',
                                                 value=[os.path.join(
                                                        pkg_irobot_create_gz_plugins,
                                                        'lib')])

    # Paths
    gz_gazebo_launch = PathJoinSubstitution(
        [pkg_ros_gz_gazebo, 'launch', 'gz_sim.launch.py'])

    # gz gazebo
    gz_gazebo_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gz_gazebo_launch]),
        launch_arguments=[
            ('gz_args', [LaunchConfiguration('world'),
                          '.sdf',
                          ' -v 4',
                          ' --gui-config ',
                          PathJoinSubstitution([pkg_irobot_create_gz_bringup, 'gui', 'create3', 'gui.config'])
                        ])
        ],
        condition=IfCondition(LaunchConfiguration('gui'))
    )

    gz_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gz_gazebo_launch]),
        launch_arguments=[
            ('gz_args', [LaunchConfiguration('world'),
                          '.sdf',
                          ' -v 4',
                          ' --gui-config ',
                        ])
        ],
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )


    # clock bridge
    clock_bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                        name='clock_bridge',
                        output='screen',
                        arguments=[
                            '/clock' + '@rosgraph_msgs/msg/Clock' + '[gz.msgs.Clock'
                        ])

    # Create launch description and add actions
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(gz_resource_path)
    ld.add_action(gz_gui_plugin_path)
    ld.add_action(gz_gazebo_gui)
    ld.add_action(gz_gazebo)
    ld.add_action(clock_bridge)
    return ld
