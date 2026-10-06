"""Receive LaserScan over rosbridge, drive the robot, and store scans."""

import argparse
import os
import queue
import threading
import time
from datetime import datetime, timezone

import roslibpy

from lds_remote.database import connect_database, save_scan
from lds_remote.scan import choose_action, normalize_scan, twist_for_action


def scan_timestamp(message):
    """Return a UTC MySQL datetime, using wall time for simulated stamps."""
    stamp = message.get("header", {}).get("stamp", {})
    seconds = stamp.get("sec", stamp.get("secs"))
    nanoseconds = stamp.get("nanosec", stamp.get("nsecs", 0))
    if seconds is None or float(seconds) < 946684800:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    timestamp = float(seconds) + float(nanoseconds) / 1_000_000_000
    return datetime.fromtimestamp(timestamp, timezone.utc).replace(tzinfo=None)


def parse_args(argv=None):
    """Parse connection, topic, and motion settings."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ros-host", default=os.environ.get("ROSBRIDGE_HOST", "localhost"))
    parser.add_argument("--ros-port", type=int, default=9090)
    parser.add_argument("--scan-topic", default="/scan")
    parser.add_argument("--cmd-topic", default="/cmd_vel")
    parser.add_argument("--no-db", action="store_true",
                        help="drive without connecting to or writing MySQL")
    parser.add_argument("--safe-distance", type=float, default=0.75)
    parser.add_argument("--linear-speed", type=float, default=0.07)
    parser.add_argument("--angular-speed", type=float, default=0.8)
    parser.add_argument("--stale-timeout", type=float, default=3.0)
    args = parser.parse_args(argv)
    if args.stale_timeout <= 0:
        parser.error("--stale-timeout must be positive")
    if args.safe_distance <= 0:
        parser.error("--safe-distance must be positive")
    if args.linear_speed < 0 or args.angular_speed < 0:
        parser.error("speeds must be non-negative")
    return args


def run():
    """Keep the control loop running until interrupted or a dependency fails."""
    args = parse_args()
    connection = None if args.no_db else connect_database()
    ros = roslibpy.Ros(host=args.ros_host, port=args.ros_port)
    incoming = queue.Queue(maxsize=256)
    queue_overflow = threading.Event()
    scan_topic = None
    cmd_topic = None
    last_received = time.monotonic()
    stopped_for_stale_scan = False

    def on_scan(message):
        try:
            incoming.put_nowait((time.monotonic(), message))
        except queue.Full:
            queue_overflow.set()

    try:
        ros.run(timeout=10)
        scan_topic = roslibpy.Topic(ros, args.scan_topic, "sensor_msgs/LaserScan")
        cmd_topic = roslibpy.Topic(ros, args.cmd_topic, "geometry_msgs/Twist")
        cmd_topic.advertise()
        scan_topic.subscribe(on_scan)
        print(f"Listening to {args.scan_topic} via ws://{args.ros_host}:{args.ros_port}", flush=True)

        while ros.is_connected:
            if queue_overflow.is_set():
                raise RuntimeError("scan queue overflow")
            try:
                received_at, message = incoming.get(timeout=0.25)
            except queue.Empty:
                if time.monotonic() - last_received >= args.stale_timeout and not stopped_for_stale_scan:
                    cmd_topic.publish(roslibpy.Message(twist_for_action("stop")))
                    stopped_for_stale_scan = True
                    print("No recent scan: stop", flush=True)
                continue

            if time.monotonic() - received_at >= args.stale_timeout:
                continue
            last_received = received_at
            try:
                ranges = normalize_scan(message)
                action = choose_action(ranges, args.safe_distance)
                measured_at = scan_timestamp(message)
            except (KeyError, TypeError, ValueError, OverflowError) as exc:
                cmd_topic.publish(roslibpy.Message(twist_for_action("stop")))
                stopped_for_stale_scan = True
                print(f"Invalid scan: {exc}; stop", flush=True)
                continue

            if connection is not None:
                save_scan(connection, ranges, action, measured_at)
            cmd_topic.publish(roslibpy.Message(twist_for_action(
                action, args.linear_speed, args.angular_speed
            )))
            stopped_for_stale_scan = False
            print(f"{measured_at.isoformat()} {action}", flush=True)
    finally:
        if cmd_topic is not None and ros.is_connected:
            cmd_topic.publish(roslibpy.Message(twist_for_action("stop")))
        if scan_topic is not None and ros.is_connected:
            scan_topic.unsubscribe()
        if cmd_topic is not None and ros.is_connected:
            cmd_topic.unadvertise()
        ros.terminate()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Stopped by user")
