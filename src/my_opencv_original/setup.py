from setuptools import setup


package_name = 'my_opencv_original'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kim',
    maintainer_email='obloodobladeo@gmail.com',
    description='Original ROS camera red line follower',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'ros_yolo_test_node = '
            'my_opencv_original.ros_yolo_test_node:main',
        ],
    },
)
