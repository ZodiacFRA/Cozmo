import asyncio
import time

import cozmo
from cozmo.objects import CustomObjectMarkers as co_markers
from cozmo.objects import CustomObjectTypes as co_types

from RobotUtils import *
from RobotActions import *
from RobotSetup import *


class Robot(object):
    def __init__(self, robot):
        self.r = robot
        self.instructions = []
        self.markers_size = 180  # mm
        self.player = None
        self.actions_library = {
            "detect_cube": [co_types.CustomType00, co_markers.Hexagons2, detect_cube],
            "approach_cube": [co_types.CustomType01, co_markers.Hexagons3, approach_cube],
            "raise_forklift": [co_types.CustomType02, co_markers.Triangles3, raise_forklift],
            "lower_forklift": [co_types.CustomType03, co_markers.Triangles4, lower_forklift],
            "turn_left": [co_types.CustomType04, co_markers.Circles2, turn_left],
            "turn_right": [co_types.CustomType05, co_markers.Circles3, turn_right],
            "move_forward": [co_types.CustomType06, co_markers.Diamonds4, move_forward],
            "move_backward": [co_types.CustomType07, co_markers.Diamonds3, move_backward],
            "EOT": [co_types.CustomType08, co_markers.Triangles2, None]
        }

    def launch(self):
        while True:
            if play_with_human():
                self.setup_game()
                self.execute_instructions()
            else: # Autonomous gameplay
                pass
            time.sleep(1)

    def execute_instructions(self):
        for instruction in self.instructions:
            if self.actions_library[2]:
                self.actions_library[2]()
