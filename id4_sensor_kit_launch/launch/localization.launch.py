from launch_ros.actions import Node
from launch import LaunchDescription
from launch_ros.actions import PushRosNamespace
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.substitutions import PathJoinSubstitution, TextSubstitution


def generate_launch_description():

    # Map paths — point to our test track map
    lanelet2_map_path    = LaunchConfiguration('lanelet2_map_path',
                            default='/autoware_map/test_track/lanelet2_map.osm')
    map_projector_path   = LaunchConfiguration('map_projector_info_path',
                            default='/autoware_map/test_track/map_projector_info.yaml')

    # ADMA topic names for ID.4
    input_topic_fix         = '/genesys/adma/fix'
    input_topic_orientation = '/sensing/gnss/ins_orientation'  # not used but required by gnss_poser arg

    declare_args = [
        DeclareLaunchArgument('lanelet2_map_path',
                              default_value='/autoware_map/test_track/lanelet2_map.osm'),
        DeclareLaunchArgument('map_projector_info_path',
                              default_value='/autoware_map/test_track/map_projector_info.yaml'),
    ]

    # Map projection loader
    map_projection_loader_include = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('autoware_map_projection_loader'),
                'launch',
                'map_projection_loader.launch.xml'
            ])
        ),
        launch_arguments={
            'map_projector_info_path': map_projector_path,
            'lanelet2_map_path':       lanelet2_map_path,
        }.items()
    )

    # Lanelet2 map loader
    lanelet2_map_loader_include = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('autoware_map_loader'),
                'launch',
                'lanelet2_map_loader.launch.xml'
            ])
        ),
        launch_arguments={
            'lanelet2_map_path': lanelet2_map_path,
        }.items()
    )

    # Lanelet2 map visualizer
    lanelet2_map_visualizer_include = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('autoware_lanelet2_map_visualizer'),
                'launch',
                'lanelet2_map_visualizer.launch.xml'
            ])
        )
    )

    # Map TF generator
    map_tf_generator_include = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('autoware_map_tf_generator'),
                'launch',
                'map_tf_generator.launch.xml'
            ])
        )
    )

    # GNSS Poser — reads /genesys/adma/fix, outputs /localization/gnss_pose_cov
    gnss_poser_include = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('autoware_gnss_poser'),
                'launch',
                'gnss_poser.launch.xml'
            ])
        ),
        launch_arguments={
            'input_topic_fix':         input_topic_fix,
            'input_topic_orientation': input_topic_orientation,
            'use_gnss_ins_orientation': 'false',
        }.items()
    )

    # GNSS pose covariance inflator
    gnss_pose_cov_inflator = Node(
        package='initial_pose_generator',
        executable='gnss_pose_cov_inflator',
        name='gnss_pose_cov_inflator',
        output='screen',
    )

    # GNSS to initial pose — fires ONCE at startup to place car on map
    gnss_to_initialpose = Node(
        package='initial_pose_generator',
        executable='gnss_to_initialpose',
        name='gnss_to_initialpose',
        output='screen',
    )

    # Odometry to twist — converts /genesys/adma/odometry to twist
    odom_to_twist = Node(
        package='odom_to_twist',
        executable='twist_with_cov',
        name='odometry_to_twist',
        output='screen',
        parameters=[{
            'input/odometry':                '/genesys/adma/odometry',
            'output/twist_with_covariance':  '/localization/twist_with_covariance',
        }]
    )

    # ADMA localization bridge — fuses pose + twist, publishes TF map→base_link
    adma_localization_bridge = Node(
        package='localization_bootstrap',
        executable='adma_localization_bridge',
        name='adma_localization_bridge',
        output='screen',
        parameters=[{
            'pose_topic':              '/localization/gnss_pose_cov',
            'twist_topic':             '/localization/twist_with_covariance',
            'map_frame':               'map',
            'base_link_frame':         'base_link',
            'publish_tf':              True,
            'time_sync_tolerance_ms':  150,
        }],
    )

    # Groups
    map_group = GroupAction([
        PushRosNamespace('map'),
        map_projection_loader_include,
        lanelet2_map_loader_include,
        lanelet2_map_visualizer_include,
        map_tf_generator_include,
    ])

    localization_group = GroupAction([
        PushRosNamespace('localization'),
        gnss_poser_include,
    ])

    return LaunchDescription(
        declare_args +
        [map_group] +
        [localization_group] +
        [gnss_pose_cov_inflator] +
        [gnss_to_initialpose] +
        [odom_to_twist] +
        [adma_localization_bridge]
    )
