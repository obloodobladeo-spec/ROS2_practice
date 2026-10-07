# 수정 전 빨간 선 주행 코드

`my_opencv_original/ros_yolo_test_node.py`는 후속 수정 전에 작성된 원본 코드를 그대로 보관합니다. 원본 파일은 화면 전체에서 빨간색을 검출하고 `/camera/image_raw`를 구독해 `/cmd_vel`을 발행합니다. ROS 2 패키지 파일은 원본을 별도 패키지로 실행할 수 있도록 추가했습니다.

## 빌드 및 실행

ROS 2 Humble 환경에서 워크스페이스 `src/` 아래에 이 패키지를 두고 실행합니다.

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select my_opencv_original
source install/setup.bash
export ROS_DOMAIN_ID=226
ros2 run my_opencv_original ros_yolo_test_node
```

카메라를 발행하는 로봇도 같은 `ROS_DOMAIN_ID`를 사용해야 합니다. 실행 전 `/camera/image_raw` 발행 여부를 확인하세요.
