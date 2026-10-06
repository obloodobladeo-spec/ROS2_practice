"""Install the JSON LaserScan replay package."""

import os
from glob import glob

from setuptools import setup

package_name = 'lds_json_replay'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kim',
    maintainer_email='obloodobladeo@gmail.com',
    description='Replay LDS JSON files on /scan.',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'json_scan_publisher = lds_json_replay.json_scan_publisher:main',
        ],
    },
)
