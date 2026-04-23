# Imports:
# --------
from setuptools import setup

package_name = 'adma_orientation_bridge'

setup(
    name=package_name,
    version='0.10.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Chidvilas Karpenahalli Ramakrishna',
    maintainer_email='Chidvilas.Karpenahalli@thi.de',
    description='ADMA heading → Autoware GnssInsOrientationStamped bridge',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'heading_to_ins_orientation = adma_orientation_bridge.heading_to_ins_orientation:main'
        ],
    },
)
