import os
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch_ros.actions import SetRemap, Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    driver_launch = os.path.join(
        get_package_share_directory('adma_ros2_driver'),
        'launch', 'adma_driver.launch.py'
    )

    sensing_group = GroupAction([
        SetRemap('/genesys/adma/data_raw',    '/sensing/gnss/data_raw'),
        SetRemap('/genesys/adma/data_scaled', '/sensing/gnss/data_scaled'),
        SetRemap('/genesys/adma/status',      '/sensing/gnss/status'),
        SetRemap('/genesys/adma/imu',         '/sensing/imu/imu_raw'),
        SetRemap('/genesys/adma/fix',         '/sensing/gnss/fix'),
        SetRemap('/genesys/adma/heading',     '/sensing/gnss/heading'),
        SetRemap('/genesys/adma/odometry',    '/sensing/gnss/odometry'),
        SetRemap('/genesys/adma/velocity',    '/sensing/gnss/velocity'),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(driver_launch)),
    ])

    bridge_node = Node(
        package='adma_orientation_bridge',
        executable='heading_to_ins_orientation',
        name='heading_to_ins_orientation',
        parameters=[{
            'heading_is_degrees': True,
            'orientation_frame': 'imu_link',
        }],
        remappings=[
            ('/genesys/adma/heading', '/sensing/gnss/heading'),
        ],
        output='screen'
    )

    return LaunchDescription([sensing_group, bridge_node])
