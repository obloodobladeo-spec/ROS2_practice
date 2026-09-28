# ROS2 C++ Publisher / Subscriber Practice

ROS2 Humble 환경에서 `turtlesim`을 이용하여 C++ 기반 Publisher와 Subscriber를 작성한 실습 프로젝트입니다.

기존 Python 기반 ROS2 노드 구조를 C++ 기반으로 변경하여 `rclcpp`의 기본 사용법과 Topic 통신 구조를 학습하는 것을 목표로 합니다.

---

## 개발 환경

- Ubuntu 22.04
- ROS2 Humble
- C++
- `rclcpp`
- `turtlesim`
- `geometry_msgs`
- `colcon`
- `ament_cmake`

---

## 패키지 구조

패키지 이름:

```text
cpp_pubsub