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
        self.cube = None
        self.actions_library = {
            "detect_cube": [co_types.CustomType00, co_markers.Hexagons2, self.detect_cube],
            "approach_cube": [co_types.CustomType01, co_markers.Hexagons3, self.approach_cube],
            "raise_forklift": [co_types.CustomType02, co_markers.Triangles3, self.raise_forklift],
            "lower_forklift": [co_types.CustomType03, co_markers.Triangles4, self.lower_forklift],
            "turn_left": [co_types.CustomType04, co_markers.Circles2, self.turn_left],
            "turn_right": [co_types.CustomType05, co_markers.Circles3, self.turn_right],
            "move_forward": [co_types.CustomType06, co_markers.Diamonds4, self.move_forward],
            "move_backward": [co_types.CustomType07, co_markers.Diamonds3, self.move_backward],
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

    def setup_game(self):
        """Wait for the player to show the instructions and
        store them till the player shows the EOT marker"""
        self.add_markers_detection()
        # Find a player
        set_to_seek_position()
        while not self.seek_player(30):
            self.robot.play_anim_trigger(cozmo.anim.Triggers.NothingToDoBoredIdle).wait_for_completed()
        # Get all instructions until EOT marker
        while self.instructions[-1] != "EOT":
            time.sleep(0.2)
        print(f"All {len(self.instructions)} instructions have been stored and will now be executed by Cozmo")

    def execute_instructions(self):
        for instruction in self.instructions:
            if self.actions_library[2]:
                self.actions_library[2]()
