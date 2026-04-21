from setuptools import find_packages, setup

package_name = 'initial_pose_generator'

setup(
    name=package_name,
    version='0.10.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='audi',
    maintainer_email='Chidvilas.Karpenahalli@thi.de',
    description='Takes initial pose from GNSS poser',
    license='Apache-v2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gnss_to_initialpose = initial_pose_generator.gnss_to_initialpose:main',
            'gnss_pose_cov_inflator = initial_pose_generator.gnss_pose_cov_inflator:main',
        ],
    },
)
