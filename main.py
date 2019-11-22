#!/usr/bin/env python3
from Robot import Robot
import cozmo

from utils import play_with_human


def main(robot: cozmo.robot.Robot):
    robot = Robot(robot, input("Player name: "))
    robot.add_markers_detection()
    robot.launch()


if __name__ == '__main__':
    cozmo.run_program(main, use_viewer=True, force_viewer_on_top=True)
