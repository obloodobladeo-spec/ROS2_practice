from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'lds_mock_ros'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'README.md'), ['README.md']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kim',
    maintainer_email='obloodobladeo@gmail.com',
    description='Randomized LaserScan publisher for ROS 2 practice.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'mock_scan_publisher = lds_mock_ros.mock_scan_publisher:main',
        ],
    },
)
