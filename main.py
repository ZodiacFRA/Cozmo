#!/usr/bin/env python3

from Robot import Robot
import cozmo


def main(robot: cozmo.robot.Robot):
    robot = Robot(robot)
    robot.launch()


if __name__ == '__main__':
    cozmo.setup_basic_logging(general_log_level="ERROR", protocol_log_level="ERROR")
    cozmo.run_program(main, use_viewer=True, force_viewer_on_top=True)
