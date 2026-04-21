from setuptools import find_packages, setup

package_name = 'odom_to_twist'

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
    maintainer='Chidvilas Karpenahalli Ramakrishna',
    maintainer_email='Chidvilas.Karpenahalli@thi.de',
    description='Converts ADMA Odometry data to Twist with Convariance',
    license='Apache-v2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'twist_with_cov = odom_to_twist.twist_with_cov:main'
        ],
    },
)
