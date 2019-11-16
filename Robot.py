import asyncio
import time

import cozmo
from cozmo.objects import CustomObject
from cozmo.objects import CustomObjectMarkers as co_markers
from cozmo.objects import CustomObjectTypes as co_types

from config import MARKERS_SIZE, ACTIONS


class Robot(object):
    def __init__(self, robot):
        self.r = robot
        self.instructions = []
        self.markers_size = 180
        self.actions_library = {
            "detect_cube": [co_types.CustomType00, co_markers.Circles3, self.do_action],
            "approach_cube": [co_types.CustomType01, co_markers.Circles3, self.do_action],
            "raise_forklift": [co_types.CustomType02, co_markers.Circles3, self.do_action],
            "lower_forklift": [co_types.CustomType03, co_markers.Circles3, self.do_action],
            "turn_left": [co_types.CustomType04, co_markers.Circles3, self.do_action],
            "turn_right": [co_types.CustomType05, co_markers.Circles3, self.do_action],
            "move_forward": [co_types.CustomType06, co_markers.Circles3, self.do_action],
            "move_backward": [co_types.CustomType07, co_markers.Circles3, self.do_action],
            "EOT": [co_types.CustomType08, co_markers.Circles3, None]
        }

    def launch(self):
        while True:
            if self.play_with_human():
                self.setup_game()
                self.execute_instructions()
            else: # Autonomous gameplay
                pass
            time.sleep(1)

    def setup_game(self):
        """Wait for the player to show the instructions and
        store them till the player shows the EOT marker"""
        self.add_markers_detection()
        while self.instructions[-1] != "EOT":
            # Wait for detection
            sleep(0.2)
        print(f"All {len(self.instructions)} instructions have been stored and will now be executed by Cozmo")

    def execute_instructions(self):
        for instruction in self.instructions:
            if self.actions_library[2]:
                self.actions_library[2]()

    def do_action(self):
        print("Not implemented yet!")

    def handle_object_appeared(self, evt, **kw):
        if isinstance(evt.obj, CustomObject):
            action_name = self.convert_obj_type_to_name(evt.obj.object_type)
            print(f"{action_name} appears")
            if self.instructions[-1] != action_name:
                self.instructions.append(action_name)

    def handle_object_disappeared(self, evt, **kw):
        if isinstance(evt.obj, CustomObject):
            print(f"{str(evt.obj.object_type)} disappear")

    def add_markers_detection(self):
        self.r.add_event_handler(cozmo.objects.EvtObjectAppeared, self.handle_object_appeared)
        self.r.add_event_handler(cozmo.objects.EvtObjectDisappeared, self.handle_object_disappeared)
        for action, marker_prop in ACTIONS.items():
            if not self.r.world.define_custom_wall(marker_prop[0], marker_prop[1],
                                                    297, 210, MARKERS_SIZE, True):
                print(f"Marker {action} definition failed!")

    def convert_obj_type_to_name(self, event_type):
        for action, prop in self.actions_library.items():
            if prop[0] == event_type:
                return action

    def __del__(self):
        """Wait for tasks completion before exiting (needed by the Cozmo SDK)"""
        time.sleep(2)
