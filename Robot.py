import asyncio
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
from cozmo.objects import CustomObjectMarkers as co_markers
from cozmo.objects import CustomObjectTypes as co_types

from utils import *


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
        if play_with_human():
            self.setup_game()
            self.execute_instructions()
        else: # Autonomous gameplay
            pass

    def setup_game(self):
        """Wait for the player to show the instructions and
        store them till the player shows the EOT marker"""
        self.add_markers_detection()
        # Find a player
        self.set_to_seek_position()
        while not self.seek_player(30):
            self.r.play_anim_trigger(cozmo.anim.Triggers.NothingToDoBoredIdle).wait_for_completed()
            time.sleep(1)
        print(f"{C_GREEN}Player found, waiting for instructions{C_RESET}")
        # Get all instructions until EOT marker
        while not len(self.instructions) or self.instructions[-1] != "EOT":
            time.sleep(0.2)
        self.instructions.pop()
        print(f"{C_GREEN}All {len(self.instructions)} instructions have been stored and will now be executed by Cozmo{C_RESET}")

    def execute_instructions(self):
        for instruction in self.instructions:
            self.actions_library[instruction][2]()

    def seek_player(self, timeout):
        look_around = self.r.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)
        try:
            self.player = self.r.world.wait_for_observed_face(timeout)
        except asyncio.TimeoutError:
            pass
        finally:  # whether we find it or not, we want to stop the behavior
            look_around.stop()

        if self.player and self.player.is_visible:
            self.r.turn_towards_face(self.player).wait_for_completed()
            self.r.play_anim_trigger(cozmo.anim.Triggers.AcknowledgeFaceNamed).wait_for_completed()
            return True
        else:
            print(f"{C_RED}Player not found{C_RESET}")

    def detect_cube(self):
        look_around = self.r.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try:
            self.cube = self.r.world.wait_for_observed_light_cube(timeout=30)
        except asyncio.TimeoutError:
            print(f"{C_RED}Cube not found{C_RESET}")
        finally:  # whether we find it or not, we want to stop the behavior
            look_around.stop()

    def approach_cube(self):
        if not self.cube:
            print(f"{C_RED}Cozmo does not remeber any cube!{C_RESET}")
        else:
            self.r.go_to_object(self.cube, distance_mm(70.0)).wait_for_completed()

    def raise_forklift(self):
        self.r.move_lift(3)

    def lower_forklift(self):
        self.r.move_lift(-3)

    def turn_left(self):
        self.r.turn_in_place(degrees(90)).wait_for_completed()

    def turn_right(self):
        self.r.turn_in_place(degrees(-90)).wait_for_completed()

    def move_forward(self):
        self.r.drive_straight(distance_mm(100), speed_mmps(100)).wait_for_completed()

    def move_backward(self):
        self.r.drive_straight(distance_mm(-100), speed_mmps(100)).wait_for_completed()

    def speak(self, msg="I don't know what to say"):
        self.r.say_text(msg).wait_for_completed()

    def convert_obj_type_to_name(self, event_type):
        for action, prop in self.actions_library.items():
            if prop[0] == event_type:
                return action

    def set_to_seek_position(self):
        """Move lift down, tilt head up"""
        self.r.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
        self.r.set_lift_height(0, in_parallel=True).wait_for_completed()

    def handle_object_appeared(self, evt, **kw):
        if isinstance(evt.obj, cozmo.objects.CustomObject):
            action_name = self.convert_obj_type_to_name(evt.obj.object_type)
            print(f"{C_BLUE}{action_name} appears{C_RESET}")
            if not len(self.instructions) or self.instructions[-1] != action_name:
                print(f"{C_GREEN}{action_name} added to the instructions list{C_RESET}")
                self.instructions.append(action_name)

    def handle_object_disappeared(self, evt, **kw):
        if isinstance(evt.obj, cozmo.objects.CustomObject):
            print(f"{C_BLUE}{self.convert_obj_type_to_name(evt.obj.object_type)} disappear{C_RESET}")

    def add_markers_detection(self):
        self.r.add_event_handler(cozmo.objects.EvtObjectAppeared, self.handle_object_appeared)
        self.r.add_event_handler(cozmo.objects.EvtObjectDisappeared, self.handle_object_disappeared)
        for action, marker_prop in self.actions_library.items():
            if not self.r.world.define_custom_wall(marker_prop[0], marker_prop[1],
                                                    297, 210, self.markers_size, True):
                print(f"{C_RED}Marker {action} definition failed!{C_RESET}")

    def __del__(self):
        """Wait for tasks completion before exiting (needed by the Cozmo SDK)"""
        time.sleep(2)
