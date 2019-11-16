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
            "detect_cube": [co_types.CustomType00, co_markers.Circles3, self.detect_cube],
            "approach_cube": [co_types.CustomType01, co_markers.Circles3, self.approach_cube],
            "raise_forklift": [co_types.CustomType02, co_markers.Circles3, self.raise_forklift],
            "lower_forklift": [co_types.CustomType03, co_markers.Circles3, self.lower_forklift],
            "turn_left": [co_types.CustomType04, co_markers.Circles3, self.turn_left],
            "turn_right": [co_types.CustomType05, co_markers.Circles3, self.turn_right],
            "move_forward": [co_types.CustomType06, co_markers.Circles3, self.move_forward],
            "move_backward": [co_types.CustomType07, co_markers.Circles3, self.move_backward],
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

    def execute_instructions(self):
        for instruction in self.instructions:
            if self.actions_library[2]:
                self.actions_library[2]()

    def detect_cube(self):
        print("Cube detection not implemented yet!")

    def approach_cube(self):
        print("Cube approach implemented yet!")

    def raise_forklift(self):
        self.robot.move_lift(3).wait_for_completed()

    def lower_forklift(self):
        self.robot.move_lift(-3).wait_for_completed()

    def turn_left(self):
        self.robot.turn_in_place(degrees(90)).wait_for_completed()

    def turn_right(self):
        self.robot.turn_in_place(degrees(-90)).wait_for_completed()

    def move_forward(self):
        self.robot.drive_straight(distance_mm(100), speed_mmps(100)).wait_for_completed()

    def move_backward(self):
        self.robot.drive_straight(distance_mm(-100), speed_mmps(100)).wait_for_completed()

    def setup_game(self):
        """Wait for the player to show the instructions and
        store them till the player shows the EOT marker"""
        self.add_markers_detection()
        while self.instructions[-1] != "EOT":
            # Wait for detection
            sleep(0.2)
        print(f"All {len(self.instructions)} instructions have been stored and will now be executed by Cozmo")

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

    def speak(self, msg="I don't know what to say"):
        self.robot.say_text(msg).wait_for_completed()

    def __del__(self):
        """Wait for tasks completion before exiting (needed by the Cozmo SDK)"""
        time.sleep(2)
