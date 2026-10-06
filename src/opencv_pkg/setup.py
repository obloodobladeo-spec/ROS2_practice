"""Install the OpenCV line follower as a ROS 2 Python package."""

from setuptools import setup

package_name = 'opencv_pkg'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['README.md']),
    ],
    install_requires=['setuptools'],
    tests_require=['pytest'],
    zip_safe=True,
    maintainer='kim',
    maintainer_email='obloodobladeo@gmail.com',
    description='Yellow line following with Gazebo camera and OpenCV.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'opencv_follow = opencv_pkg.opencv_follow:main',
            'camera_cv_bridge = opencv_pkg.camera_cv_bridge:main',
            'camera_numpy = opencv_pkg.camera_numpy:main',
        ],
    },
)
