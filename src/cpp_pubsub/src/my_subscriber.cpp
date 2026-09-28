#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"

class TurtlePoseSubscriber : public rclcpp::Node
{
public:
    TurtlePoseSubscriber()
    : Node("turtle_pose_subscriber")
    {
        subscription_ =
            this->create_subscription<turtlesim::msg::Pose>(
                "/turtle1/pose",
                10,
                std::bind(
                    &TurtlePoseSubscriber::pose_callback,
                    this,
                    std::placeholders::_1
                )
            );
    }

private:
    void pose_callback(const turtlesim::msg::Pose & msg)
    {
        RCLCPP_INFO(
            this->get_logger(),
            "x: %.2f, y: %.2f, theta: %.2f, linear_velocity: %.2f, angular_velocity: %.2f",
            msg.x,
            msg.y,
            msg.theta,
            msg.linear_velocity,
            msg.angular_velocity
        );
    }

    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<TurtlePoseSubscriber>();

    rclcpp::spin(node);

    rclcpp::shutdown();

    return 0;
}